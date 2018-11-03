

import paho.mqtt.publish as publish
import json

class MQTT:
    def __init__(self, mqtthostname, myhostname, devicename):
        self.mqtthostname = mqtthostname
        self.myhostname = myhostname
        self.devicename = devicename
        print("Connecting to MQTT at: %s" % self.mqtthostname)

    def publishString(self, verb, message):
        publish.single("%s/%s/%s" % (verb, self.myhostname, self.devicename), message, hostname=self.mqtthostname)

    def publish(self, verb, obj):
        obj['device'] = self.devicename
        self.publishString(verb, json.dumps(obj))