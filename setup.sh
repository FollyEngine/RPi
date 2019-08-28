#!/bin/bash

for pkg in $(find -maxdepth 1 -type d); do
    if [[ "$pkg" == "." ]]; then
        continue
    fi
    echo "setup /src/$pkg/setup.sh"

	if [[ -f "/src/$pkg/requirements.txt" ]]; then
		pip install --no-cache-dir -r /src/$pkg/requirements.txt;
		pip3 install --no-cache-dir -r /src/$pkg/requirements.txt;
	fi
	if [[ -f "/src/$pkg/setup.sh" ]]; then
		/src/$pkg/setup.sh;
	fi
done