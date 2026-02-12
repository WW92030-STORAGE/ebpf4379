import subprocess, math

VA_ORDER = 48       # How many bits does the address space occupy?

from execute import exec_
import CONSTANTS

# Init a profile with evenly spread ranges and default benefit. 
def set_all_zeros(BUCKET_ORDER = CONSTANTS.BUCKET_ORDER, benefit = 200000):
    # BUCKET_ORDER is the log of how many buckets there are.
    BUCKET_SHIFT = 48 - BUCKET_ORDER    # Log of how big each bucket is
    NUM_BUCKETS = 1 << BUCKET_ORDER  
    BUCKET_SIZE = 1 << BUCKET_SHIFT   # how big the bucket is, in terms of powers of 2 of the bucket size

    cmd = "echo \"%d\" | sudo tee /proc/set_prof_size" % (NUM_BUCKETS)
    exec_(cmd)

    for i in range(NUM_BUCKETS):
        # set the start

        START = i * BUCKET_SIZE
        END = START + BUCKET_SIZE - 1

        # set the start
        cmd = "echo \"%d %d\" | sudo tee /proc/set_starts" % (i, START)
        exec_(cmd)

        # set the end
        cmd = "echo \"%d %d\" | sudo tee /proc/set_ends" % (i, END)
        exec_(cmd)

        # set the benefit
        cmd = "echo \"%d %d\" | sudo tee /proc/set_benefits" % (i, benefit)
        exec_(cmd)

        if i % int(math.sqrt(NUM_BUCKETS)) == 0:
            print("INIT VALUE ... " + str(i) + "/" + str(NUM_BUCKETS))
    
    print("INIT DONE")


if __name__ == "__main__":
    set_all_zeros()