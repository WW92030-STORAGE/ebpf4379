#!/bin/bash

NTHREADS=2
NDOCS=131072

cd mongodb-benchmarking

./mongo-bench -threads $NTHREADS -docs $NDOCS -uri mongodb://localhost:27017 -type insert
./mongo-bench -threads $NTHREADS -docs $NDOCS -uri mongodb://localhost:27017 -type update
./mongo-bench -threads $NTHREADS -docs $NDOCS -uri mongodb://localhost:27017 -type upsert
./mongo-bench -threads $NTHREADS -docs $NDOCS -uri mongodb://localhost:27017 -type delete

echo "MONGODB WORKFLOW DONE"