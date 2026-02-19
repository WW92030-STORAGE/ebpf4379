#!/bin/bash

sudo apt update
sudo apt install -y build-essential linux-tools-common linux-tools-generic
sudo cp /usr/lib/linux-tools-6.8.0-100/perf /usr/bin