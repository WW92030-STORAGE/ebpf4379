#!/bin/bash

sudo python3 init_values.py

echo "BENEFITS RESET"

#!/usr/bin/env bash
set -euo pipefail

setsid sudo python3 address_hist.py &
FOREVER_PID=$!

cd .. &

sudo python3 tester.py &
TERM_PID=$!

wait "$TERM_PID"

kill -- -"$FOREVER_PID"