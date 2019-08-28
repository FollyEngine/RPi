#!//usr/bin/python3

import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
import traceback
from time import sleep

allMuted = False
repeats = {}


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import mqtt
import config

myHostname = config.getValue("hostname", socket.gethostname())

master_mqtt_host = config.getValue("mqttmaster", "mqtt.thegame.folly.site")
mastermqtt = mqtt.MQTT(master_mqtt_host, myHostname, "relay_to", "everyone", "S4C7Tzjc2gD92y9", 1883)
#mastermqtt.loop_start()   # use the background thread

# end load config

mastermqtt.status({"status": "listening"})
mastermqtt.publish("hello", {"once":"we"})

try:
    #while True:
    #    sleep(1)
    mastermqtt.loop_forever()
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")

#hostmqtt.status({"status": "STOPPED"})
mastermqtt.status({"status": "STOPPED"})
