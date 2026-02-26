from bcc import BPF
from CONSTANTS import BUCKET_ORDER, BUCKET_SHIFT, BUCKET_SIZE, NUM_BUCKETS
from time import sleep
import time
import argparse, subprocess, atexit
from execute import exec_
import math

# FAULT HISTOGRAM

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

# PROMOTION HISTOGRAM


promotion_histogram_program = """
#include <uapi/linux/ptrace.h>
#include <linux/mm.h>

BPF_ARRAY(addr_hist, u64, """ + str(NUM_BUCKETS) + """);

int probe_create_huge_pmd(struct pt_regs *ctx)
{
    struct vm_fault* vmf;

    unsigned long addr = 0;
    
    vmf = (struct vm_fault *)PT_REGS_PARM1(ctx);
    bpf_probe_read_kernel(&addr, sizeof(addr), &vmf->address);

    u64 bucket = addr >> """ + str(BUCKET_SHIFT) + """;

    if (bucket >= """ + str(NUM_BUCKETS) + """)
        bucket = """ + str(NUM_BUCKETS) + """ - 1;   // clamp

    u64 *val = addr_hist.lookup(&bucket);
    if (val)
        __sync_fetch_and_add(val, 1);

    return 0;
}
"""

promo_b = BPF(text=promotion_histogram_program)
promo_b.attach_kprobe(event="do_huge_pmd_anonymous_page", fn_name="probe_create_huge_pmd")

# Procure and return the histograms
def print_linear_hist(clear_hist = True):
    # print("---- Linear VA Fault Histogram ----")
    fault_arr = fault_b.get_table("addr_hist")
    promo_arr = promo_b.get_table("addr_hist")

    fault_res = []
    promo_res = []

    for i, v in fault_arr.items():
        count = v.value
        if count == 0:
            continue

        start = i.value * BUCKET_SIZE
        end = start + BUCKET_SIZE - 1

        # print("%#16x - %#16x : %d" % (start, end, count))

        fault_res.append((start, end, count))
    for i, v in promo_arr.items():
        count = v.value
        if count == 0:
            continue

        start = i.value * BUCKET_SIZE
        end = start + BUCKET_SIZE - 1

        # print("%#16x - %#16x : %d" % (start, end, count))

        promo_res.append((start, end, count))
    if clear_hist:
        fault_arr.clear()
        promo_arr.clear()

    return fault_res, promo_res

# Convert the histogram, (start, end, count), into a flat histogram with implicitly defined ranges as indices.
def get_bucket_info(val):
    res = [0] * NUM_BUCKETS
    for input in val:
        bucket_index = input[0] >> BUCKET_SHIFT

        res[bucket_index] = input[2]
    return res

# Constants and globals

# Transition array: [AAccesses, FFaults, PPromotions]
prior_transition_array = None
prior_histograms = None

# Metrics
prior_fault_bi = [0] * NUM_BUCKETS
prior_promo_bi = [0] * NUM_BUCKETS

fault_decrease_numerator = 0
fault_decrease_denominator = 0
fdn_histo = [0] * NUM_BUCKETS
fdd_histo = [0] * NUM_BUCKETS


perf_rec = None

UPDATE_HISTOS = False

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
    MODE = "progressive"

    parser = argparse.ArgumentParser(description = "put pid here")
    parser.add_argument('--workflow', type=str, default = "")

    args = parser.parse_args()
    workflow_pid = args.workflow

    print("PID:", workflow_pid)

    while True:
        # Begoin damo record

        sleep(PERIOD)

        # End damo record

        START = time.perf_counter_ns()

        # Convert the histogram
        fault, promo = print_linear_hist()
        fault_bi = get_bucket_info(fault)
        promo_bi = get_bucket_info(promo)

        print("FF", [str(i) + ": " + str(fault_bi[i]) + " | " for i in range(len(fault_bi)) if fault_bi[i] != 0])
        print("PP", [str(i) + ": " + str(promo_bi[i]) + " | " for i in range(len(promo_bi)) if promo_bi[i] != 0])

        # do profiling here



        
        END = time.perf_counter_ns()
        ELAPSED_NS = END - START
        print("COLLECT MS:", ELAPSED_NS * 0.000001)


        if UPDATE_HISTOS:
            if MODE == "radicalist" or MODE == "progressive":
                if prior_transition_array is None:
                    prior_transition_array = [0] * NUM_BUCKETS
                if prior_histograms is None:
                    prior_histograms = []

                pta = [i for i in prior_transition_array]
                
                RUNNING_WINDOW = 8
                prior_histograms.append(fault_bi)
                for i in range(NUM_BUCKETS):
                    prior_transition_array[i] += fault_bi[i]
                
                while len(prior_histograms) > RUNNING_WINDOW:
                    ph = prior_histograms[0]
                    prior_histograms = prior_histograms[1:]

                    for i in range(NUM_BUCKETS):
                        prior_transition_array[i] -= ph[i]

                if MODE == "radicalist":
                    for i in range(NUM_BUCKETS):
                        # increasing in faults
                        # print(pta[i], prior_transition_array[i])
                        if prior_transition_array[i] > pta[i]:
                            cmd = "echo \"%d %d\" | sudo tee /proc/set_benefits" % (i, 400000)
                            exec_(cmd)
                        elif prior_transition_array[i] < pta[i]:
                            cmd = "echo \"%d %d\" | sudo tee /proc/set_benefits" % (i, 100000)
                            exec_(cmd)
                if MODE == "progressive":
                    for i in range(NUM_BUCKETS):
                        # increasing in faults
                        # print(pta[i], prior_transition_array[i])
                        diff = prior_transition_array[i] - pta[i]

                        # diff = math.sqrt(diff)

                        diff = int(diff)
                        if diff != 0:
                            cmd = "echo \"%d %d %d\" | sudo tee /proc/increase_benefits" % (i, abs(diff), diff >= 0)
                            exec_(cmd)

        # Begin evaluate metrics

        for i in range(NUM_BUCKETS):
            if prior_promo_bi[i] > 0:
                fault_decrease_denominator += 1
                fdd_histo[i] += 1
                if fault_bi[i] < prior_fault_bi[i]:
                    fault_decrease_numerator += 1
                    fdn_histo[i] += 1

        
        prior_fault_bi = [i for i in fault_bi]
        prior_promo_bi = [i for i in promo_bi]

        # End evaluate metrics

        END = time.perf_counter_ns()
        ELAPSED_NS = END - START
        print("FULL MS:", ELAPSED_NS * 0.000001)


        if fault_decrease_denominator > 0:
            print("FAULT DECREASE RATE: " + str(fault_decrease_numerator / fault_decrease_denominator))

        print("FD", [str(i) + ": " + f"{(fdn_histo[i] / fdd_histo[i]):.4f}" + " | " for i in range(len(fdd_histo)) if fdd_histo[i] != 0])

        print("------------\n\n------------")

                

            
                



"""

WHAT WE WANT

More promotions implies: 1. Less faults 2. More accesses

"""

def goodbye():
    global perf_rec
    print("HISTOGRAM TERMINATED")
    if perf_rec:
        perf_rec.terminate()

def exit_handler():
    goodbye()

atexit.register(exit_handler)