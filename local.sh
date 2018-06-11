#!/bin/bash -ex

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
	nohup python rfid/main.py $MQTTHOST > rfid.log &
	nohup python audio/main.py $MQTTHOST > audio.log &
	nohup python controller/main.py $MQTTHOST > controller.log &

	echo "DONE"
	exit
fi

# otherwise, setup..

git pull
	
# get pyscard
sudo apt-get update \
&& sudo apt-get upgrade -yq \
    && sudo apt-get install -yq python-pyscard python-pip pcscd git python-setuptools libpcsclite-dev python-dev mosquitto-clients mosquitto

cd rfid
sudo pip install --no-cache-dir -r requirements.txt

