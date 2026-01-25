from bcc import BPF
from time import sleep

from execute import exec_

"""

Address histogram. Intermittently, it procures a histogram of address ranges that were affected the most. 
Look into accesses as well?

"""

from CONSTANTS import BUCKET_ORDER, BUCKET_SHIFT, BUCKET_SIZE, NUM_BUCKETS

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
    while True:
        sleep(4)
        val = print_linear_hist()

        bucket_info = get_bucket_info(val)

        count = sum(x != 0 for x in bucket_info)
        if count:
            mu = sum(bucket_info) / count
            for index in range(len(bucket_info)):
                if bucket_info[index] == 0:
                    continue
                elif bucket_info[index] > mu:
                    cmd = "echo \"%d %d\" | sudo tee /proc/set_benefits" % (index, 400000)
                    exec_(cmd)
                elif bucket_info[index] < mu:
                    cmd = "echo \"%d %d\" | sudo tee /proc/set_benefits" % (index, 100000)
                    exec_(cmd)


