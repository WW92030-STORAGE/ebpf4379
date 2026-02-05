from bcc import BPF
from time import sleep

from execute import exec_
import random

import concurrent.futures as CF
import time

"""

Address histogram. Intermittently, it procures a histogram of address ranges that were affected the most. 
Look into accesses as well?

"""

from CONSTANTS import BUCKET_ORDER, BUCKET_SHIFT, BUCKET_SIZE, NUM_BUCKETS
from UTILS import get_benefits

# Actual eBPF system that procure the histogram

prog = """
#include <uapi/linux/ptrace.h>

BPF_ARRAY(addr_hist, u64, """ + str(NUM_BUCKETS) + """);

int probe_handle_mm_fault(struct pt_regs *ctx)
{
    
    unsigned long addr = PT_REGS_PARM2(ctx);
    u64 bucket = addr >> """ + str(BUCKET_SHIFT) + """;

    if (bucket >= """ + str(NUM_BUCKETS) + """)
        bucket = """ + str(NUM_BUCKETS) + """ - 1;   // clamp

    u64 *val = addr_hist.lookup(&bucket);
    if (val)
        __sync_fetch_and_add(val, 1);

    return 0;
}
"""

b = BPF(text=prog)
b.attach_kprobe(event="handle_mm_fault", fn_name="probe_handle_mm_fault")

print("Tracing... Ctrl-C to stop.")

# Procure and return the histogram
def print_linear_hist():
    # print("---- Linear VA Fault Histogram ----")
    arr = b.get_table("addr_hist")

    res = []

    for i, v in arr.items():
        count = v.value
        if count == 0:
            continue

        start = i.value * BUCKET_SIZE
        end = start + BUCKET_SIZE - 1

        # print("%#16x - %#16x : %d" % (start, end, count))

        res.append((start, end, count))
    arr.clear()

    return res

# Convert the histogram, (start, end, count), into a flat histogram with implicitly defined ranges as indices.
def get_bucket_info(val):
    res = [0] * NUM_BUCKETS
    for input in val:
        bucket_index = input[0] >> BUCKET_SHIFT

        res[bucket_index] = input[2]
    return res

# Constants and globals

prior_histogram = None

# Runner -- periodically procure a histogram and do updates
if __name__ == "__main__":
    """

    Period = seconds per iteration
    FIXED_VALUES = Whether we fall to the prototype or use the dynamic updates
    PARALLEL = Whether we parallelize some operations
    TRADE_VALUE = How much is brought over from the lower-than-avg to the higher-than-avg
    UB/LB - Attempts to change benefits to outside this range are ignored.

    """
    PERIOD = 8
    FIXED_VALUES = False
    PARALLEL = True
    NUM_THREADS = 4
    TRADE_VALUE = 5000
    while True:
        sleep(PERIOD)

        START = time.perf_counter_ns()

        # Convert the histogram
        val = print_linear_hist()
        bucket_info = get_bucket_info(val)

        # Count (baseline for averages)
        count = sum(x != 0 for x in bucket_info)

        END = time.perf_counter_ns()
        ELAPSED_NS = END - START
        print("XEBPF_COUNT MS:", ELAPSED_NS * 0.000001)

        if count:
            # average number of hits
            mu = sum(bucket_info) / count

            # Fixed benefits (cut and dry) or dynamic updates?
            if FIXED_VALUES:
                for index in range(len(bucket_info)):
                    if bucket_info[index] == 0:
                        continue
                    elif bucket_info[index] > mu:
                        cmd = "echo \"%d %d\" | sudo tee /proc/set_benefits" % (index, 400000)
                        exec_(cmd)
                    elif bucket_info[index] < mu:
                        cmd = "echo \"%d %d\" | sudo tee /proc/set_benefits" % (index, 100000)
                        exec_(cmd)
            else:

                sum_below_avg = 1
                sum_above_avg = 1
                for index in range(NUM_BUCKETS):
                    deviation = abs(bucket_info[index] - mu)
                    if bucket_info[index] == 0:
                        continue
                    elif bucket_info[index] > mu:
                        sum_above_avg += deviation
                    elif bucket_info[index] < mu:
                        sum_below_avg += deviation
                
                def modify_worker(start_val, step):
                    for index in range(start_val, NUM_BUCKETS, step):
                        deviation = abs(bucket_info[index] - mu)
                        transfer = (TRADE_VALUE * deviation) // sum_above_avg
                        if bucket_info[index] == 0:
                            continue
                        if bucket_info[index] + transfer > mu:
                            cmd = "echo \"%d %d %d\" | sudo tee /proc/increase_benefits" % (index, transfer, 1)
                            exec_(cmd)
                        elif bucket_info[index] < mu:
                            cmd = "echo \"%d %d %d\" | sudo tee /proc/increase_benefits" % (index, transfer, 0)
                            exec_(cmd)
                if not PARALLEL:
                    modify_worker(0, 1)
                else:
                    with CF.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                        for i in range(NUM_THREADS):
                            executor.submit(modify_worker, i, NUM_THREADS)
        
        END = time.perf_counter_ns()
        ELAPSED_NS = END - START
        print("FULL MS:", ELAPSED_NS * 0.000001)



