
RFIDIMAGE="realengine/rfid"

run:
	docker run --rm -it  --privileged -v /dev/bus/usb:/dev/bus/usb $(RFIDIMAGE)

shell:
	docker run --rm -it  --privileged -v /dev/bus/usb:/dev/bus/usb $(RFIDIMAGE) bash

build:
	docker build -t $(RFIDIMAGE) rfid
