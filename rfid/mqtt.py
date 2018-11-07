

import paho.mqtt.client as mqttclient
import json
import traceback

class MQTT:
    def __init__(self, mqtthostname, myhostname, devicename):
        self.mqtthostname = mqtthostname
        self.myhostname = myhostname
        self.devicename = devicename
        self.sub = {}
        self.connect()

    def status(self, obj):
        obj['device'] = self.devicename
        global client
        client.publish("%s/%s/%s" % (self.myhostname, self.devicename, 'status'), payload=json.dumps(obj), retain=True)

    def publishString(self, host, device, verb, message):
        global client
        client.publish("%s/%s/%s" % (host, device, verb), message)

    def publishL(self, host, device, verb, obj):
        obj['device'] = self.devicename
        self.publishString(host, device, verb, json.dumps(obj))

    def publish(self, verb, obj):
        obj['device'] = self.devicename
        self.publishString(self.myhostname, self.devicename, verb, json.dumps(obj))

    def subscribeL(self, host, device, verb, function=""):
        global client
        sub_topic = "%s/%s/%s" % (host, device, verb)
        client.subscribe(sub_topic)
        print("Subscribed to %s" % sub_topic)
        self.sub[sub_topic] = function

    def subscribe(self, verb, function=""):
        self.subscribeL(self.myhostname, self.devicename, verb, function)

    def connect(self):
        global client
        #TODO: can we ask what clients are connected and detect collisions?
        clientname="%s_%s" % (self.myhostname, self.devicename)
        client = mqttclient.Client(clientname)
        #client.on_message=on_message #attach function to callback
        client.on_disconnect=self.on_disconnect
        self.set_on_message(self.on_message)
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

    def decode(self, raw):
        return json.loads(raw)

    #TODO: this happens when a message failed to be sent - need to resend it..
    def on_disconnect(self, innerclient, userdata,rc=0):
        print("DisConnected result code "+str(rc))
        client.reconnect()
        client.publish("status", {"status": "reconnecting"})

#class Object(object):
#    pass
#a = Object()
#a.topic = "Podium5/audio/play"
#a.payload = '{"sound": "'+testsound+'"}'
#hostmqtt.on_message(mqtt.client, '', a)
    def on_message(self, client, userdata, message):
        print("on_message %s" % message.topic)
        #print("message received " ,payload)
        #print("message topic=",message.topic)
        #print("message qos=",message.qos)
        #print("message retain flag=",message.retain)

        message_func = ""
        try:
            if message.topic in self.sub:
                message_func = self.sub[message.topic]
                print("direct")
            else:
                for t in self.sub:
                    if self.topic_matches_sub(t, message.topic):
                        message_func = self.sub[t]
                        print("match")
                        break

            print("asd")
            print(message_func)
            if message_func == "":
                print("No message_func found for %s" % message.topic)
                return

            raw_payload=str(message.payload.decode("utf-8"))
            print("HHRAW: "+message.topic+": "+raw_payload)

            if raw_payload == "" or raw_payload == "REMOVED" or raw_payload == "(null)":
                return

            payload = self.decode(raw_payload)
            print("DECODED: "+message.topic+": "+str(payload))
            message_func(message.topic, payload)
        except Exception as e:
            print("exception:")
            traceback.print_exc()
