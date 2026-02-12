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
import UTILS

import histograms as hists

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
        val = hists.print_linear_hist()[0]
        bucket_info = hists.get_bucket_info(val)



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

        # Compute trends i guess

        if hists.prior_transition_array is not None:
            cosine = UTILS.cosine_sim(bucket_info, hists.prior_transition_array)
            print("COSINE SIM", cosine)

            emd_Score = UTILS.emd(bucket_info, hists.prior_transition_array)
            print("EMD", emd_Score)

        hists.prior_transition_array = bucket_info

        
        END = time.perf_counter_ns()
        ELAPSED_NS = END - START
        print("FULL MS:", ELAPSED_NS * 0.000001)



"""

If a certain page is below the average but all are very high
We could include zero hit pages?
We could split this between 0 and nonzero pages

DS's proposal: 

Instead of comparing benefits, think of if a page should have been promoted
Use the new histogram to evaluate the decisions made on a page. If a page was promoted previously, its access count should be higher.

Loop (every period):

1. Compute the histogram
2. Compute a uhh transition array. This represents how the promoted page regions change e.g. benefit changes, boolean whatevers, etc.
3. Use the histogram, and analyze the previous transition array instead of the previous histogram.

Use absolute thresholds e.g. the page regions hould have 100 or soaccesses in teh last preiod (or i guess per second)



"""




"""

Known guardrail strategies
- Increase/benefit benefits based on above/below average number of region hits (does not work for mongodb)

"""