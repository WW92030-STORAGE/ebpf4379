#!/bin/bash


# https://github.com/ctch3ng/Installing-Python-2.7-and-pip-on-Ubuntu-24.04-Noble-LTS
sudo apt install -y default-jdk
sudo apt install -y build-essential checkinstall libncurses-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev libreadline-dev libdb-dev

cd /usr/src
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
tar xzf Python-2.7.18.tgz
cd Python-2.7.18
./configure --prefix=/usr/local/python2.7
make
sudo make install
echo 'export PATH="/usr/local/python2.7/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc