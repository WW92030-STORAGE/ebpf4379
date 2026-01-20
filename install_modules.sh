#!/bin/bash

# /proc/set_benefits
cd setbenefits_mod
make
sudo insmod setbenefits_mod.ko

# /proc/set_ends
cd ../setends_mod
make
sudo insmod setends_mod.ko
make clean

# /proc/set_estimate
cd ../setestimate_mod
make
sudo insmod setestimate_mod.ko
make clean

# /proc/set_prof_size
cd ../setpsize_mod
make
sudo insmod setpsize_mod.ko
make clean

# /proc/set_starts
cd ../setstarts_mod
make
sudo insmod setstarts_mod.ko
make clean

# /proc/force_init
cd ../forceinit_mod
make
sudo insmod forceinit_mod.ko
make clean

# /proc/increase_benefits
cd ../incbenefits_mod
make
sudo insmod incbenefits_mod.ko
make clean


# echo ? ? | sudo tee /proc/set_???