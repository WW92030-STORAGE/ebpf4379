#!/bin/bash

WARMUPS=4
TESTS=16

./install_workload.sh

cd ycsb-mongodb-binding-0.17.0

# ./bin/ycsb load mongodb-async -s -P workloads/workloada
./bin/ycsb run mongodb-async -s -P workloads/workloada & 
PID2=$!

cd ../../profile
sudo python3 histograms.py --workflow $PID2  & 
PID=$!

echo "Histogram updater: $PID" 

wait $PID2

echo "DONE"

sudo kill $PID
wait $PID

echo "FIN"