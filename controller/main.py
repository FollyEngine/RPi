import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
#from subprocess import call
import yaml

#######
# load config (extract to lib)
configFile = "config.yml"
if len(sys.argv) > 1:
    configFile = sys.argv[1]

with open(configFile, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

mqttHost = "mqtt"
if "mqtthostname" in cfg and cfg["mqtthostname"] != "":
    mqttHost = cfg["mqtthostname"]

myHostname = socket.gethostname()
if "hostname" in cfg and cfg["hostname"] != "":
    myHostname = cfg["hostname"]
# end load config


############
def play(audiofile):
   publish.single("follyengine/"+myHostname+"/play", audiofile, hostname=mqttHost)

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

            audiofile = "test.wav"
            if "default" in cfg["pillars"]:
                if "(null)" in cfg["pillars"]["default"]:
                    audiofile = cfg["pillars"]["default"]["(null)"]
            if "default" in cfg["pillars"]:
                if item in cfg["pillars"]["default"]:
                    audiofile = cfg["pillars"]["default"][item]
            if myHostname in cfg["pillars"]:
                if item in cfg["pillars"][myHostname]:
                    audiofile = cfg["pillars"][myHostname][item]

            play(audiofile)
            
            # neopixels
            if "sparkles" in cfg:
                if item == cfg["sparkles"]:
                    client.publish("follyengine/"+myHostname+"/neopixel", item)

    except:
        return
########################################

client = mqtt.Client(myHostname+"_controller") #create new instance
client.on_message=on_message #attach function to callback

print("Connecting to MQTT at: %s" % mqttHost)
client.connect(mqttHost) #connect to broker

client.subscribe("follyengine/"+myHostname+"/rfid")

client.publish("status/"+myHostname+"/controller","STARTED")
publish.single("follyengine/"+myHostname+"/test", "test", hostname=mqttHost)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exit")

client.publish("status/"+myHostname+"/controller","STOPPED")
