from bcc import BPF
from CONSTANTS import BUCKET_ORDER, BUCKET_SHIFT, BUCKET_SIZE, NUM_BUCKETS

fault_histogram_program = """
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

fault_b = BPF(text=fault_histogram_program)
fault_b.attach_kprobe(event="handle_mm_fault", fn_name="probe_handle_mm_fault")

# Procure and return the histogram
def print_linear_hist(clear_hist = True):
    # print("---- Linear VA Fault Histogram ----")
    arr = fault_b.get_table("addr_hist")

    res = []

    for i, v in arr.items():
        count = v.value
        if count == 0:
            continue

        start = i.value * BUCKET_SIZE
        end = start + BUCKET_SIZE - 1

        # print("%#16x - %#16x : %d" % (start, end, count))

        res.append((start, end, count))
    if clear_hist:
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

prior_transition_array = None

# Runner -- periodically procure a histogram and do updates
if __name__ == "__main__":
    """

    Period = seconds per iteration
    FIXED_VALUES = Whether we fall to the prototype or use the dynamic updates
    PARALLEL = Whether we parallelize some operations
    TRADE_VALUE = How much is brought over from the lower-than-avg to the higher-than-avg
    UB/LB - Attempts to change benefits to outside this range are ignored.

    """
    PERIOD = 4
    FIXED_VALUES = False
    PARALLEL = True
    NUM_THREADS = 4
    TRADE_VALUE = 10000
    while True:
        sleep(PERIOD)

        START = time.perf_counter_ns()

        # Convert the histogram
        val = print_linear_hist()
        bucket_info = get_bucket_info(val)

        print("HISTOGRAM", bucket_info)


        # do profiling here

        
        END = time.perf_counter_ns()
        ELAPSED_NS = END - START
        print("FULL MS:", ELAPSED_NS * 0.000001)