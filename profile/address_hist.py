from bcc import BPF
from time import sleep

"""

Address histogram. Intermittently, it procures a histogram of address ranges that were affected the most. 

"""

# choose a sane number of buckets
BUCKET_ORDER = 6                    # Log of how many buckets there are 
BUCKET_SHIFT = 48 - BUCKET_ORDER    # Log of how big each bucket is
NUM_BUCKETS = 1 << BUCKET_ORDER  
BUCKET_SIZE = 1 << BUCKET_SHIFT   # how big the bucket is, in terms of powers of 2 of the bucket size

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
    print("---- Linear VA Fault Histogram ----")
    arr = b.get_table("addr_hist")

    res = []

    for i, v in arr.items():
        count = v.value
        if count == 0:
            continue

        start = i.value * BUCKET_SIZE
        end = start + BUCKET_SIZE - 1

        print("%#16x - %#16x : %d" % (start, end, count))

        res.append((start, end, count))
    arr.clear()

    return res


if __name__ == "__main__":
    while True:
        sleep(4)
        val = print_linear_hist()

        print(val)
