#!/bin/bash

echo "VALUES RESET"

sudo rm perf.data
sudo rm perf.data.old
perf buildid-cache --purge-all


# do stuff here
cd ..
./mongobench_run.sh & 
PID2=$!

echo "Workflow: $PID2"

cd profile

sudo python3 histograms.py --workflow $PID2  & 
PID=$!

echo "Histogram updater: $PID" 

wait $PID2

echo "DONE"

sudo kill $PID
wait $PID

echo "FIN"