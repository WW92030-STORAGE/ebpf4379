VA_ORDER = 48       # How many bits does the address space occupy?
# choose a sane number of buckets
BUCKET_ORDER = 7                    # Log of how many buckets there are 
BUCKET_SHIFT = 48 - BUCKET_ORDER    # Log of how big each bucket is
NUM_BUCKETS = 1 << BUCKET_ORDER  
BUCKET_SIZE = 1 << BUCKET_SHIFT   # how big the bucket is, in terms of powers of 2 of the bucket size

'''

What will also be useful: come up with a system/architecture diagram showing how everything links up

Where, what, when, and how of different elements in the arch

'''
