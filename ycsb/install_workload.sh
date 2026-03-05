#!/bin/bash

mongosh ycsb --eval "db.usertable.drop()"
cd ycsb-mongodb-binding-0.17.0
./bin/ycsb load mongodb-async -s -P workloads/workloada