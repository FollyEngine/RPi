import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
#from subprocess import call
import yaml

with open("config", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

mqttHost = "mqtt"

myHostname = socket.gethostname()
sounddir = '/mnt/'
testsound='test.wav'


############
def play(audiofile):
   publish.single("follyengine/"+myHostname+"/play", audiofile, hostname=mqttHost)
   #publish.single("follyengine/"+mqttHost+"/play", audiofile, hostname=mqttHost)


############
def on_message(client, userdata, message):
    payload=str(message.payload.decode("utf-8"))
    print("")
    print("message received " ,payload)
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

    try:
        if mqtt.topic_matches_sub("follyengine/all/rfid", message.topic):
            # everyone
            print("everyone plays "+payload)
            play(payload)
        elif mqtt.topic_matches_sub("follyengine/"+myHostname+"/rfid", message.topic):
            item = cfg["items"][payload]
            print(myHostname+" got "+payload+" which is: "+item)
            try:
                play(cfg["pillars"]["default"][item])
            except:
                play(cfg["pillars"]["default"]["(null)"])
    except:
        return
########################################

if len(sys.argv) > 1:
    mqttHost = sys.argv[1]
if len(sys.argv) > 2:
    sounddir = sys.argv[2]


client = mqtt.Client(myHostname+"_controller") #create new instance
client.on_message=on_message #attach function to callback

print("Connecting to MQTT at: %s" % mqttHost)
client.connect(mqttHost) #connect to broker

client.subscribe("follyengine/"+myHostname+"/rfid")

client.publish("status/"+myHostname+"/controller","STARTED")
play(testsound)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exit")

client.publish("status/"+myHostname+"/controller","STOPPED")
