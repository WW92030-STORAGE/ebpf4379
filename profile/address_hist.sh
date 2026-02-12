#!/bin/bash

sudo python3 init_values.py

echo "VALUES RESET"

sudo python3 histograms.py 1>/dev/null 2>/dev/null & 
PID=$!

echo "Histogram updater: $PID" 


# do stuff here
cd ..
./mongobench_run.sh & 
PID2=$!

echo "Workflow: $PID"

wait $PID2

echo "DONE"

kill $PID