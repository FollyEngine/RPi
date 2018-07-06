#!/bin/bash -ex

git pull
cd ../convictshope
git pull

PODIUM=$(cat /mnt/podium.name | sed 's/^hostname: //g')

echo "Podium: $PODIUM"
