

import paho.mqtt.client as mqttclient
import json

organisation = "follyengine"


class MQTT:
    def __init__(self, mqtthostname, myhostname, devicename):
        self.mqtthostname = mqtthostname
        self.myhostname = "%s_%s" %(myhostname, devicename)
        self.devicename = devicename
        self.connect()

    def publishString(self, verb, message):
        global client
        client.publish("%s/%s/%s" % (organisation, self.myhostname, verb), message)

    def publish(self, verb, obj):
        obj['device'] = self.devicename
        self.publishString(verb, json.dumps(obj))

    def subscribe(self, topic):
        global client
        client.subscribe(topic)

    def connect(self):
        global client
        client = mqttclient.Client(self.myhostname)
        #client.on_message=on_message #attach function to callback
        client.on_disconnect=on_disconnect

        print("Connecting to MQTT at: %s" % self.mqtthostname)
        client.connect(self.mqtthostname)

    def set_on_message(self, on_message):
        global client
        client.on_message=on_message #attach function to callback

    def loop_forever(self):
        global client
        client.loop_forever()

    def topic_matches_sub(self, sub, topic):
        return mqttclient.topic_matches_sub(sub, topic)

# TODOL move this back into the class
def on_disconnect(client, userdata,rc=0):
    print("DisConnected result code "+str(rc))
    client.reconnect()
    client.publish("status", {"status": "reconnecting"})

