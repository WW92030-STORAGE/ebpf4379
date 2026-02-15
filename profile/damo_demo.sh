#!/bin/bash

DAMO_REC="damon.data"

# do stuff here
cd ..
./mongobench_run.sh & 
PID2=$!

echo "Workflow: $PID2"

sudo damo start

sudo damo record $PID2 -o $DAMO_REC & 
DAMO_PID=$!

echo "DAMO: $DAMO_PID"

wait $PID2

echo "DONE"

if kill -0 $DAMO_PID 2>/dev/null; then
    sudo kill -INT "$DAMO_PID"
    wait "$DAMO_PID" || true
fi

sudo damo report

sudo damo stop