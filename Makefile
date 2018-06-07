
RFIDIMAGE="realengine/rfid"

stack: build
	docker stack up -c mq_net.yml mq
	docker stack up -c mq_server.yml mqs

mq_ping:
	docker run --rm -it --network mq_net mosquitto-clients mosquitto_pub -h mqs_server  -t 'hello' -m 'world'

run:
	docker run --rm -it  --privileged -v /dev/bus/usb:/dev/bus/usb $(RFIDIMAGE)

shell:
	docker run --rm -it  --privileged -v /dev/bus/usb:/dev/bus/usb $(RFIDIMAGE) bash

build:
	docker build -t mosquitto-clients mosquitto-clients
	docker build -t $(RFIDIMAGE) rfid

push:
	docker push ${RFIDIMAGE}

