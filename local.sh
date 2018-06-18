#!/bin/bash -ex

# default MQTTHOST to `mqtt` as a default
export MQTTHOST='mqtt'

# do we have a cfg sdcard?
if sudo fdisk -l | grep sda1 | grep FAT32; then
	if ! mount | grep mnt | cut -d ' ' -f 1 | grep /dev/sda1; then
		sudo mount /dev/sda1 /mnt
	fi
	source /mnt/config.sh
fi

echo "MQTT at $MQTTHOST"
echo "this host called $HOSTNAME"

# 
if [[ ¨$1¨ != ¨--setup¨ ]]; then

	sleep 10
	ping -c 1 $MQTTHOST

	/usr/bin/nohup python rfid/main.py $MQTTHOST > rfid.log &
	/usr/bin/nohup python audio/main.py $MQTTHOST > audio.log &
	/usr/bin/nohup python controller/main.py $MQTTHOST > controller.log &

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
