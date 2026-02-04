from bcc import BPF
from time import sleep

from execute import exec_
import random

import concurrent.futures as CF

"""

Address histogram. Intermittently, it procures a histogram of address ranges that were affected the most. 
Look into accesses as well?

"""

from CONSTANTS import BUCKET_ORDER, BUCKET_SHIFT, BUCKET_SIZE, NUM_BUCKETS
from UTILS import get_benefits

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

def get_bucket_info(val):
    res = [0] * NUM_BUCKETS
    for input in val:
        bucket_index = input[0] >> BUCKET_SHIFT

        res[bucket_index] = input[2]
    return res

if __name__ == "__main__":
    PERIOD = 8
    FIXED_VALUES = False
    PARALLEL = True
    NUM_THREADS = 8
    TRADE_VALUE = 5000
    UB = 400000 - 20000
    LB = 20000
    while True:
        sleep(PERIOD)
        val = print_linear_hist()

        bucket_info = get_bucket_info(val)
        count = sum(x != 0 for x in bucket_info)
        if count:
            mu = sum(bucket_info) / count
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
                
                def partial_mod(start_val, step):
                    for index in range(start_val, NUM_BUCKETS, step):
                        deviation = abs(bucket_info[index] - mu)
                        if bucket_info[index] == 0:
                            continue
                        cur_ben = get_benefits(index)
                        if bucket_info[index] > mu:
                            if cur_ben > UB:
                                continue
                            cmd = "echo \"%d %d %d\" | sudo tee /proc/increase_benefits" % (index, (TRADE_VALUE * deviation) // sum_above_avg, 1)
                            exec_(cmd)
                        elif bucket_info[index] < mu:
                            if cur_ben < UB:
                                continue
                            cmd = "echo \"%d %d %d\" | sudo tee /proc/increase_benefits" % (index, (TRADE_VALUE * deviation) // sum_below_avg, 0)
                            exec_(cmd)
                if not PARALLEL:
                    for index in range(NUM_BUCKETS):
                        deviation = abs(bucket_info[index] - mu)
                        if bucket_info[index] == 0:
                            continue
                        cur_ben = get_benefits(index)
                        if bucket_info[index] > mu:
                            if cur_ben > UB:
                                continue
                            cmd = "echo \"%d %d %d\" | sudo tee /proc/increase_benefits" % (index, (TRADE_VALUE * deviation) // sum_above_avg, 1)
                            exec_(cmd)
                        elif bucket_info[index] < mu:
                            if cur_ben < UB:
                                continue
                            cmd = "echo \"%d %d %d\" | sudo tee /proc/increase_benefits" % (index, (TRADE_VALUE * deviation) // sum_below_avg, 0)
                            exec_(cmd)
                else:
                    with CF.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                        for i in range(NUM_THREADS):
                            executor.submit(partial_mod, i, NUM_THREADS)


