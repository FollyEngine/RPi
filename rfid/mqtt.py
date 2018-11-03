

import paho.mqtt.client as mqtt
import json

class MQTT:
    def __init__(self, mqtthostname, myhostname, devicename):
        self.mqtthostname = mqtthostname
        self.myhostname = "%s_%s" %(myhostname, devicename)
        self.devicename = devicename
        self.connect()

    def publishString(self, verb, message):
        self.client.publish("%s/%s/%s" % (verb, self.myhostname, self.devicename), message)

    def publish(self, verb, obj):
        obj['device'] = self.devicename
        self.publishString(verb, json.dumps(obj))

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def connect(self):
        self.client = mqtt.Client(self.myhostname)
        #client.on_message=on_message #attach function to callback
        self.client.on_disconnect=self.on_disconnect

        print("Connecting to MQTT at: %s" % self.mqtthostname)
        self.client.connect(self.mqtthostname)

    def set_on_message(self, on_message):
        self.client.on_message=on_message #attach function to callback

    def on_disconnect(client, userdata,rc=0):
        print("DisConnected result code "+str(rc))
        #client.loop_stop()
