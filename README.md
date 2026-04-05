# ebpf4379

`sudo apt-get install python3-bpfcc linux-headers-$(uname -r)`

You must build [github.com/WW92030-STORAGE/scea_linux/](github.com/WW92030-STORAGE/scea_linux/) first! See `LINUX.md` for details.

NOTE - The following word salad is not a `bash` file. There are multiple branches as well as portions that you must do outside of running commands.

```

# ENTER THIS FOLDER (e.g.)

cd ebpf4379

# SETUP MONGO

sudo chmod -R 777 . && sudo ./install_modules.sh && ./mongo_install.sh

# SETUP PERF/DAMO

sudo ./install_perf.sh && sudo ./install_damo.sh

# SETUP YCSB

cd ycsb
sudo ./install_python.sh && ./install_mongo4.sh && ./install_ycsb.sh
echo 'export PATH="/usr/local/python2.7/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# RUN MONGO (4.2)

./run_mongo4.sh

# RUN TESTS
# 1. First, make sure mongo and modules are installed, and mongo 4.2 is running. Then, there are two branches:

# A. IF YOU ARE RUNNING CBMM:
cd ~/ebpf4379/profile
# change NO_UPDATES in damon_report_only.py to True
sudo echo 0 > /proc/force_init
cd ../ycsb

# B. IF YOU ARE RUNNING AN ADAPTIVE POLICY
cd ~/ebpf4379/profile
# change NO_UPDATES in damon_report_only.py to False
# change the value in init_values.py and damon_report_only.py marked by CHANGE THE DEFAULT VALUE HERE to whatever is needed. 200000 and below is no promotions, anything above means promotions.
# EMPTY THE damo_report.txt FILE
sudo python3 init_values.py

# 2. Then, run the actual workload.
cd ../ycsb

# If you have not installed the workload
./install_workload.sh

# Run the actual workload.
./run_tests.sh

```