#!/bin/bash

set -e

# install deb packages
xargs -a deb-packages.txt sudo apt install
# install pip for python3
sudo apt install python3-pip
# install dependancies
python3 -m pip install --upgrade pip
if [ -f requirements.txt ]; then python3 -m pip install -r requirements.txt; fi
# ensure scripts are executable
chmod +x run-rcs.sh
chmod +x run-tcs.sh
