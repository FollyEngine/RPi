FROM alpine:edge
MAINTAINER David Audet <david.audet@ca.com>

LABEL Description="Eclipse Mosquitto MQTT Clients"

RUN apk --no-cache add mosquitto-clients=1.4.15-r3

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["mosquitto_sub", "-h", "mqs_server", "-v", "-t", "#"]
