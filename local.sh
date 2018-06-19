#!/bin/bash -ex

CONFIGFILE="$(pwd)/config.yml"

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
	sleep 10
	ping -c 1 $MQTTHOST

	/usr/bin/nohup python rfid/main.py $CONFIGFILE > rfid.log 2>&1 &
	/usr/bin/nohup python audio/main.py $CONFIGFILE > audio.log 2>&1 &
	/usr/bin/nohup python controller/main.py $CONFIGFILE > controller.log 2>&1 &
	/usr/bin/nohup sudo python neopixels/main.py $CONFIGFILE > neopixel.log 2>&1 &

	echo "DONE"
	exit
fi

# otherwise, setup..

git pull
	
# get pyscard
sudo apt-get update
sudo apt-get upgrade -yq
sudo apt-get install -yq python-pyscard python-pip pcscd git python-setuptools libpcsclite-dev python-dev mosquitto-clients mosquitto scratch python-pygame

cd rfid
sudo pip install --no-cache-dir -r requirements.txt
cd ../audio
sudo pip install --no-cache-dir -r requirements.txt
cd ../controller
sudo pip install --no-cache-dir -r requirements.txt
cd ..
