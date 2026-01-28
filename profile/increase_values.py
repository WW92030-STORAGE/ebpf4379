import subprocess

VA_ORDER = 48       # How many bits does the address space occupy?

from execute import exec_
import CONSTANTS

# Init a profile with evenly spread ranges and default benefit. 
def increase_constant(BUCKET_ORDER = CONSTANTS.BUCKET_ORDER, benefit = 10000):
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

        # set the benefit
        cmd = "echo \"%d %d %d\" | sudo tee /proc/increase_benefits" % (i, benefit, 1)
        exec_(cmd)


if __name__ == "__main__":
    increase_constant()