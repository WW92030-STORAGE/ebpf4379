#!/bin/bash

NTHREADS=16
NDOCS=1048576
NDOCS=65536

cd mongodb-benchmarking

./mongo-bench -threads $NTHREADS -docs $NDOCS -uri mongodb://localhost:27017 -type insert
./mongo-bench -threads $NTHREADS -docs $NDOCS -uri mongodb://localhost:27017 -type update
./mongo-bench -threads $NTHREADS -docs $NDOCS -uri mongodb://localhost:27017 -type upsert
./mongo-bench -threads $NTHREADS -docs $NDOCS -uri mongodb://localhost:27017 -type delete

echo "MONGODB WORKFLOW DONE"


# look at the pid