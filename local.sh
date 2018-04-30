#!/bin/bash -ex

# test to see if the first arg is a pingable host
if [[ ¨$1¨ != ¨¨ ]]; then
	if ping -c1 $1; then
		# if it is, run service
		exec python rfid/main.py $@
	fi
fi

# otherwise, setup..
	
# get pyscard
sudo apt-get update \
    && sudo apt-get install -yq python-pyscard python-pip pcscd git python-setuptools libpcsclite-dev python-dev

cd rfid
sudo pip install --no-cache-dir -r requirements.txt

