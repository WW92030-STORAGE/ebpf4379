#!/bin/bash

PERF_REC="perf.out"
ORDER=8
N_BUCKETS=$(( 1 << $ORDER ))
BUCKET_SIZE=$(( 0x1000000000000 >> $ORDER ))
ADDR_SPACE=$(( 1<<48 ))

echo "BUCKET_SIZE: $BUCKET_SIZE"

# do stuff here
PPWWDD=$(pwd)
cd ..
./mongobench_run.sh & 
PID2=$!

echo "Workflow: $PID2"

sudo perf mem record -a &
PERF_PID=$!

echo "PERF: $PERF_PID"

wait $PID2

sudo kill -INT $PERF_PID

wait $PERF_PID

echo "DONE"

cd $PPWWDD

perf script | sudo tee $PERF_REC > /dev/null

echo "FIN"