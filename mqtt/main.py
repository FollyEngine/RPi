#!//usr/bin/python3

import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
import traceback

allMuted = False
repeats = {}


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import mqtt
import config

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "relay_from")

master_mqtt_host = config.getValue("mqttmaster", "mqtt.thegame.folly.site")
#mastermqtt = mqtt.MQTT(master_mqtt_host, myHostname, "relay_to", "everyone", "S4C7Tzjc2gD92y9", 80, "websockets")
mastermqtt = mqtt.MQTT(master_mqtt_host, myHostname, "relay_to", "everyone", "S4C7Tzjc2gD92y9", 8883)

# end load config

############
def muteAll():
    hostmqtt.publishL("all", "audio", "mute", {})

########################################################
# subscription handlers

def relay_message(topic, payload):
    # TODO: need to add a "relayed from X message, so we don't make a relay loop"
    mastermqtt.publish(topic, payload)

########################################

hostmqtt.subscribeL("+", "status", "+", relay_message)

hostmqtt.publish("status", {"status": "listening"})


try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.publish("status",{"status": "STOPPED"})
