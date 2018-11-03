

import paho.mqtt.client as mqttclient
import json

class MQTT:
    def __init__(self, mqtthostname, myhostname, devicename):
        self.mqtthostname = mqtthostname
        self.myhostname = myhostname
        self.devicename = devicename
        self.connect()

    def publishString(self, verb, message):
        global client
        client.publish("%s/%s/%s" % (self.myhostname, self.devicename, verb), message)

    def publish(self, verb, obj):
        obj['device'] = self.devicename
        self.publishString(verb, json.dumps(obj))

    def subscribe(self, verb):
        self.subscribeL(self.myhostname, self.devicename, verb)

    def subscribeL(self, host, device, verb):
        global client
        client.subscribe("%s/%s/%s" % (host, device, verb))

    def connect(self):
        global client
        #TODO: can we ask what clients are connected and detect collisions?
        clientname="%s_%s" % (self.myhostname, self.devicename)
        client = mqttclient.Client(clientname)
        #client.on_message=on_message #attach function to callback
        client.on_disconnect=on_disconnect

        print("Connecting to MQTT as %s at: %s" % (clientname, self.mqtthostname))
        client.connect(self.mqtthostname)

    def set_on_message(self, on_message):
        global client
        client.on_message=on_message #attach function to callback

    def loop_forever(self):
        global client
        client.loop_forever()

    def topic_matches_sub(self, sub, topic):
        return mqttclient.topic_matches_sub(sub, topic)

#TODO: move this back into the class
#TODO: this happens when a message failed to be sent - need to resend it..
def on_disconnect(client, userdata,rc=0):
    print("DisConnected result code "+str(rc))
    client.reconnect()
    client.publish("status", {"status": "reconnecting"})

