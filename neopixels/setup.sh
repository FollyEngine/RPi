#!/bin/bash


sudo pip3 install --no-cache-dir -r ./src/RPi/neopixels/requirements.txt

cd
if [[ -d rpi_ws2810 ]]; then
	cd rpi_ws281x
	git pull
else
	git clone https://github.com/jgarff/rpi_ws281x
	cd rpi_ws281x
fi


sudo apt-get install -yq scons gcc
scons

cd python
sudo apt-get install -yq python3-dev swig

python3 ./setup.py build
sudo python3 ./setup.py install

