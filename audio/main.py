import paho.mqtt.client as mqtt #import the client1
import time
import sys
from subprocess import call
import pygame

host="hostname"
testsound='/app/test.wav'

pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

############
def play(audiofile):
    # TODO: if its a URL, download it (unless we already have it)
    #call(['/usr/bin/paplay', audiofile])
    pygame.mixer.music.load(audiofile)
    pygame.mixer.music.play()


############
def on_message(client, userdata, message):
    payload=str(message.payload.decode("utf-8"))
    print("")
    print("message received " ,payload)
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    if mqtt.topic_matches_sub("play/all", message.topic):
        # everyone
        print("everyone plays "+payload)
        play(payload)
    elif mqtt.topic_matches_sub("play/test", message.topic):
        print("everyone plays test.wav")
        play(testsound)
    elif mqtt.topic_matches_sub("play/"+host, message.topic):
        print(host+" plays "+payload)
        play(payload)

########################################
broker_address="mqs_server"
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker

client.subscribe("#")
client.publish("status/"+host+"/audio","STARTED")

pygame.mixer.music.load(testsound)
pygame.mixer.music.play()

while True:
    try:
        client.loop()
    except KeyboardInterrupt:
        print("exit")
        sys.exit()

client.publish("status/"+host+"/audio","STOPPED")
