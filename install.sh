#!/bin/bash

##System update
sudo apt-get update
sudo apt-get upgrade
##install required packages.
#!Check if python3-libcamera is necessary for ennv
sudo apt-get install python3 python3-pip python3-venv libcap-dev libcamera-dev libkms++-dev libfmt-dev libdrm-dev libgl1_mesa_glx

#Enter venv and activate packages.
python -m venv venv
sourve ./venv/bin/activate
python -m pip install -r ./software/requirements
deactivate
echo "Successfully installed the phoenix project! Try it out with "./software/start.sh"