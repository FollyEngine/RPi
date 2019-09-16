#!/bin/bash

# used to install scratch to get lots of wav files, but its 400MB
sudo DEBIAN_FRONTEND=noninteractive apt-get install -yq python3-pyo

sudo pip3 install --no-cache-dir -r ./audio/requirements.txt


