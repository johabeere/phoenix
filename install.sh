#!/bin/bash

#TODO add build script. Needs the "libcap development headers". 
##System update
apt-get update
apt-get upgrade
##install required packages.
#!Check if python3-libcamera is necessary for ennv
apt-get install python3 python3-pip python3-venv libcap-dev libcamera-dev libkms++-dev libfmt-dev libdrm-dev libgl1_mesa_glx
python -m venv venv
sourve ./venv/bin/activate
pip install .........

### !!!! rpi-libcamera needs to be installed as rpi-libcamera==0.1a3!!!!! ###  
###pip packages: rpi-kms rpi-libcamera==0.1a3 numpy