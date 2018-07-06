#!/bin/bash -ex

git pull
cd ../convictshope
git pull

sudo rsync * /mnt/

PODIUM=$(cat /mnt/podium.name | sed 's/^hostname: //g')

echo "Podium: $PODIUM"

cat config.yml | sed "s/^hostname: .*$/hostname: $PODIUM/g" > /tmp/config.yml
sudo cp /tmp/config.yml /mnt/config.yml
