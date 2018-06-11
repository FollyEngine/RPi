import paho.mqtt.client as mqtt #import the client1
import time
import sys
import socket
from subprocess import call
import pygame

mqttHost = "mqtt"

hostname = socket.gethostname()
sounddir = '/mnt/'
testsound='test.wav'

pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

############
def play(audiofile):
    # TODO: if its a URL, download it (unless we already have it)
    #call(['/usr/bin/paplay', audiofile])
    if not audiofile.startswith('/'):
        audiofile = sounddir + audiofile

    pygame.mixer.music.load(audiofile)
    pygame.mixer.music.play()

############
def on_disconnect(client, userdata,rc=0):
    logging.debug("DisConnected result code "+str(rc))
    #client.loop_stop()

############
def on_message(client, userdata, message):
    payload=str(message.payload.decode("utf-8"))
    print("")
    print("message received " ,payload)
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    if mqtt.topic_matches_sub("follyengine/all/play", message.topic):
        # everyone
        print("everyone plays "+payload)
        play(payload)
    elif mqtt.topic_matches_sub("follyengine/all/test", message.topic):
        print("everyone plays test.wav")
        play(testsound)
    elif mqtt.topic_matches_sub("follyengine/"+hostname+"/play", message.topic):
        print(hostname+" plays "+payload)
        play(payload)

########################################

if len(sys.argv) > 1:
    mqttHost = sys.argv[1]
if len(sys.argv) > 2:
    sounddir = sys.argv[2]


client = mqtt.Client(hostname+"_audio") #create new instance
client.on_message=on_message #attach function to callback
client.on_disconnect=on_disconnect

print("Connecting to MQTT at: %s" % mqttHost)
client.connect(mqttHost) #connect to broker

client.subscribe("follyengine/"+hostname+"/play")
client.subscribe("follyengine/+/test")

client.publish("status/"+hostname+"/audio","STARTED")

play(testsound)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exit")

client.publish("status/"+host+"/audio","STOPPED")
