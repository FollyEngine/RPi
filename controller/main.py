import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
from subprocess import call

mqttHost = "mqtt"

myHostname = socket.gethostname()
sounddir = '/mnt/'
testsound='test.wav'

pillar = {}
pillar["REMOVED"] = "/usr/share/scratch/Media/Sounds/Vocals/BeatBox1.wav"
pillar["(null)"] = "/usr/share/scratch/Media/Sounds/Vocals/BeatBox2.wav"

pillar["2A70F8A3"] = "/usr/share/scratch/Media/Sounds/Animal/Bird.wav"
pillar["1A3602A4"] = "/usr/share/scratch/Media/Sounds/Animal/Dog1.wav"
pillar["8A6BFFA3"] = "/usr/share/scratch/Media/Sounds/Animal/Duck.wav"
pillar["8AF5FCA3"] = "/usr/share/scratch/Media/Sounds/Animal/Goose.wav"
pillar["5ABB02A4"] = "/usr/share/scratch/Media/Sounds/Animal/HorseGallop.wav"
pillar["1A6A00A4"] = "/usr/share/scratch/Media/Sounds/Animal/Kitten.wav"
pillar["AA7EF5A3"] = "/usr/share/scratch/Media/Sounds/Animal/Owl.wav"
pillar["9B1147EC"] = "/usr/share/scratch/Media/Sounds/Animal/Rooster.wav"
pillar["FBD221EC"] = "/usr/share/scratch/Media/Sounds/Animal/WolfHowl.wav"
#pillar[""] = "/usr/share/scratch/Media/Sounds/"



############
def play(audiofile):
   #publish.single("follyengine/"+myHostname+"/play", audiofile, hostname=mqttHost)
   publish.single("follyengine/"+mqttHost+"/play", audiofile, hostname=mqttHost)


############
def on_message(client, userdata, message):
    payload=str(message.payload.decode("utf-8"))
    print("")
    print("message received " ,payload)
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

    if mqtt.topic_matches_sub("follyengine/all/rfid", message.topic):
        # everyone
        print("everyone plays "+payload)
        play(payload)
    elif mqtt.topic_matches_sub("follyengine/"+mqttHost+"/rfid", message.topic):
        print(myHostname+" got "+payload)
        try:
            play(pillar[payload])
        except:
            play(pillar["(null)"])
    elif mqtt.topic_matches_sub("follyengine/"+myHostname+"/rfid", message.topic):
        print(myHostname+" got "+payload)
        try:
            play(pillar[payload])
        except:
            play(pillar["(null)"])

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

#client.publish("status/"+myHostname+"/controller","STARTED")
#play(testsound)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exit")

client.publish("status/"+myHostname+"/controller","STOPPED")
