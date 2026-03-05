#!/bin/bash
sudo chmod -R 777 .
cd ycsb
sudo ./install_python.sh && ./install_mongo4.sh && ./install_ycsb.sh && ./run_mongo4.sh
