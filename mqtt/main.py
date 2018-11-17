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

def relay_message_to_master(topic, payload):
    # Only relay messages from our local mqtt to the global one if they havn't already been relayed
    if not "relay_from" in payload:
        payload["relay_from"] = myHostname
        mastermqtt.relay(topic, payload)

def relay_message_from_master(topic, payload):
    # Only relay messages from our local mqtt to the global one if they havn't already been relayed
    if not "relay_from" in payload:
        payload["relay_from"] = master_mqtt_host
    else:
        if payload["relay_from"] == myHostname:
            # don't relay a message that originated with us...
            return

    mastermqtt.relay(topic, payload)

########################################


hostmqtt.subscribeL("+", "status", "+", relay_message_to_master)
mastermqtt.subscribeL("+", "+", "+", relay_message_from_master)

hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})
