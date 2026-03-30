#!/bin/bash

PWDIR=$(pwd)

cd

wget https://www.openssl.org/source/openssl-1.1.1w.tar.gz
tar -xvf openssl-1.1.1w.tar.gz
cd openssl-1.1.1w

./config --prefix=$HOME/openssl-1.1
make -j$(nproc)
make install

cd $PWDIR
wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1804-4.2.24.tgz
tar -xvf mongodb-linux-x86_64-ubuntu1804-4.2.24.tgz
cd mongodb-linux-x86_64-ubuntu1804-4.2.24/bin

LD_LIBRARY_PATH=~/openssl-1.1/lib ./mongodb-linux-x86_64-ubuntu1804-4.2.24/bin/mongod --dbpath database