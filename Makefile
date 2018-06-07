.PHONY: audio

RFIDIMAGE="realengine/rfid"
ID:=$(shell id -u)

stack: build
	docker stack up -c mq_net.yml mq
	docker stack up -c mq_server.yml mqs

mq_ping:
	docker run --rm -it --network mq_net mosquitto-clients mosquitto_pub -h mqs_server  -t 'hello' -m 'world'

audio:
	docker run --rm -it \
		-v pulseaudio:/run/pulse \
		--user 1000 \
		-v $(PWD)/audio/:/app \
		--network mq_net \
		audio

run:
	docker run --rm -it  --privileged -v /dev/bus/usb:/dev/bus/usb $(RFIDIMAGE)

shell:
	docker run --rm -it  --privileged -v /dev/bus/usb:/dev/bus/usb $(RFIDIMAGE) bash

build:
	docker build -t mosquitto-clients mosquitto-clients
	docker build -t $(RFIDIMAGE) rfid
	docker build -t audio audio

push:
	docker push ${RFIDIMAGE}


make-pulseaudio-volume:
	docker volume rm pulseaudio || true
	docker volume create --opt type=none --opt device=/run/user/$(ID)/pulse/ --opt o=bind pulseaudio

