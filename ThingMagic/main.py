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
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "ThingMagic")

import mercury

# end load config

########################################

def rfidTagDataCallback(rfid):
    try:
        hostmqtt.publish("scan", {
                'atr': rfid.epc_mem_data,
                'tag': rfid.epc.hex(),
                'rssi': rfid.rssi,
                'event': 'inserted'
            })

        print("EPC: %s RSSI: %s\n" % (rfid.epc, rfid.rssi))
        print("     epc_mem_data: %s" % rfid.epc_mem_data)
        print("     tid_mem_data: %s" % rfid.tid_mem_data)
        print("     user_mem_data: %s" % rfid.user_mem_data)
        print("     reserved_mem_data: %s" % rfid.reserved_mem_data)
    except Exception as ex:
        traceback.print_exc()


########################################

reader = mercury.Reader("tmr:///dev/ttyACM0")

reader.set_region("AU")
reader.set_read_plan([1], "GEN2")


print(reader.get_model())
print(reader.get_antennas())
print(reader.get_read_powers())

hostmqtt.status({"status": "listening"})
reader.start_reading(rfidTagDataCallback, on_time=100, off_time=0)
while True:
    try:
        time.sleep(1)
        print(".")
        #print(reader.read())
    except KeyboardInterrupt:
        print("exit")
        reader.stop_reading()
        break

hostmqtt.status({"status": "STOPPED"})
