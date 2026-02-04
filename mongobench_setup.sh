#!/bin/bash

sudo apt install -y golang-go
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.25.6.linux-amd64.tar.gz
go version

cd mongodb-benchmarking
make build