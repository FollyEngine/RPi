#!/bin/bash -ex

CONFIGFILE="$(pwd)/config.yml"
DATE=$(date +%Y-%m-%d-%H.%M)

# do we have a cfg sdcard?
if sudo fdisk -l | grep sda1 | grep FAT32; then
	if ! mount | grep mnt | cut -d ' ' -f 1 | grep /dev/sda1; then
		sudo mount /dev/sda1 /mnt
	fi
	FILE="/mnt/config.yml"
	if [[ -f "$FILE" ]]; then
		CONFIGFILE="$FILE"
	fi
fi

MQTTHOST=$(grep mqtthostname: $CONFIGFILE | sed 's/mqtthostname: //')
HOSTNAME=$(grep hostname: $CONFIGFILE | sed 's/mqtthostname: //')

echo "using cfg from $CONFIGFILE"
echo "MQTT at $MQTTHOST"
echo "this host called $HOSTNAME"

# 
if [[ ¨$1¨ != ¨--setup¨ ]]; then
	sleep 15
	ping -c 1 $MQTTHOST

	python3 rfid/main.py $CONFIGFILE > rfid-${DATE}.log 2>&1 &
	python3 audio/main.py $CONFIGFILE > audio-${DATE}.log 2>&1 &
	python3 controller/main.py $CONFIGFILE > controller-${DATE}.log 2>&1 &
	#/usr/bin/nohup sudo python neopixels/main.py $CONFIGFILE > neopixel-${DATE}.log 2>&1 &
	python3 rmeote /main.py $CONFIGFILE > rmeote-${DATE}.log 2>&1 &
	sudo python3 remote/main.py $CONFIGFILE /dev/input/by-id/usb-AleTV_Remote_V1_RF_USB_Controller-event-mouse > rmeote-mouse-${DATE}.log 2>&1 &

	echo "DONE"
	exit
fi

# otherwise, setup..

# get pyscard
sudo apt-get update
sudo apt-get upgrade -yq
sudo apt-get install -yq python3-pyscard python3-pip pcsc-tools pcscd git python3-setuptools libpcsclite-dev python3-dev \
			mosquitto-clients mosquitto scratch python-pygame

git pull

cd rfid
sudo pip3 install --no-cache-dir -r requirements.txt
cd ../audio
sudo pip3 install --no-cache-dir -r requirements.txt
cd ../controller
sudo pip3 install --no-cache-dir -r requirements.txt
cd ../remote
sudo pip3 install --no-cache-dir -r requirements.txt
cd ..

cat /proc/device-tree/model
if grep "Raspberry Pi" /proc/device-tree/model; then
	if ! lsmod | grep hifiberry; then
		echo "installing drivers for pHAT"
		curl https://get.pimoroni.com/phatdac | bash
	fi
fi
