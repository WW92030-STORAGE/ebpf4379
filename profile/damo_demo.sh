#!/bin/bash

DAMO_REC="damon.data"
ORDER=8
N_BUCKETS=$(( 1 << $ORDER ))
BUCKET_SIZE=$(( 0x1000000000000 >> $ORDER ))
ADDR_SPACE=$(( 1<<48 ))

echo "BUCKET_SIZE: $BUCKET_SIZE"

# do stuff here
cd ..
./mongobench_run.sh & 
PID2=$!

echo "Workflow: $PID2"

sudo damo start
sudo damo tune --minr $N_BUCKETS --maxr $N_BUCKETS --damos_sz_region $BUCKET_SIZE $BUCKET_SIZE
sudo damo tune --regions "0-$ADDR_SPACE"

sudo damo tune --ops vaddr --sample 5000 --aggr 100000 --updr 1000000 --minr 10 --maxr 1000

sudo damo stop

sudo damo record $PID2 -o $DAMO_REC & 
DAMO_PID=$!

echo "DAMO: $DAMO_PID"

wait $PID2

echo "DONE"

if kill -0 $DAMO_PID 2>/dev/null; then
    sudo kill -INT "$DAMO_PID"
    wait "$DAMO_PID" || true
fi

sudo damo report heats