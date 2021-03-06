.PHONY: audio

HUBORG="follyengine"

RFIDIMAGE="$(HUBORG)/rfid"
ID:=$(shell id -u)
# linux/arm64
PLATFORMS="linux/amd64,linux/arm/v7,linux/arm/v6"

audio:
	docker run -it \
		--device /dev/snd \
		-e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
		-v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
		-v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
		--group-add $(shell getent group audio | cut -d: -f3) \
		--network mq_net \
		-v $(PWD)/audio/:/app \
			audio

audio-shell:
	docker run --rm -it \
		-v pulseaudio:/run/pulse \
		--user 1000 \
		-v $(PWD)/audio/:/app \
		--network mq_net \
		audio bash

run:
	docker run --rm -it  --privileged -v /dev/bus/usb:/dev/bus/usb $(RFIDIMAGE)

shell:
	docker run --rm -it  --privileged -v /dev/bus/usb:/dev/bus/usb $(RFIDIMAGE) bash

build: build-base build-ping build-neopixels build-rfid-d10x build-audio build-crickit

build-base:
	docker buildx build --platform $(PLATFORMS) --pull --push -t $(HUBORG)/base -f Dockerfile.base .

build-ping:
	docker buildx build --platform $(PLATFORMS) --pull --push -t $(HUBORG)/ping -f Dockerfile.ping .

build-neopixels:
	docker buildx build --platform $(PLATFORMS) --pull --push -t $(HUBORG)/neopixels -f Dockerfile.neopixels .

build-rfid-d10x:
	docker buildx build --platform $(PLATFORMS) --pull --push -t $(HUBORG)/rfid-d10x -f Dockerfile.rfid-d10x .

build-audio:
	docker buildx build --platform $(PLATFORMS) --pull --push -t $(HUBORG)/audio:pyo -f Dockerfile.audio .

build-crickit:
	docker buildx build --platform $(PLATFORMS) --pull --push -t $(HUBORG)/crickit:latest -f Dockerfile.crickit .

make-pulseaudio-volume:
	docker volume rm pulseaudio || true
	docker volume create --opt type=none --opt device=/run/user/$(ID)/pulse/ --opt o=bind pulseaudio

