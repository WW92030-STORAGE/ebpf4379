#!/bin/bash

sudo python3 init_values.py
cd ..
sudo python3 profile/address_hist.py & sudo python3 youlostthegame.py

wait