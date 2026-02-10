from bcc import BPF
from time import sleep

from execute import exec_
import random

import concurrent.futures as CF
import time

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
    PERIOD = 16
    FIXED_VALUES = False
    PARALLEL = True
    NUM_THREADS = 4
    TRADE_VALUE = 10000
    while True:
        sleep(PERIOD)

        START = time.perf_counter_ns()

        # Convert the histogram
        val = hists.print_linear_hist()
        bucket_info = hists.get_bucket_info(val)

        print("FAULT HIST", bucket_info)


        # do profiling here

        
        END = time.perf_counter_ns()
        ELAPSED_NS = END - START
        print("FULL MS:", ELAPSED_NS * 0.000001)



"""

Keep track of the following per period:
1. Address regions histogram (fault counts)
2. Which pages were promoted during this period (???)
3. The number of huge pages in each region. Compare the huge page count with teh fault counts 

In the histogram count the promotions per region. Then for each region, compute the promotion / fault(or access) ratio

"""




"""

Known guardrail strategies
- Increase/benefit benefits based on above/below average number of region hits (does not work for mongodb)

"""