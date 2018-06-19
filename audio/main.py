import paho.mqtt.client as mqtt #import the client1
import time
import sys
import socket
import pygame
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

sounddir = '/mnt/'
if "sounddir" in cfg and cfg["sounddir"] != "":
    sounddir = cfg["sounddir"]
testsound='test.wav'
if "testsound" in cfg and cfg["testsound"] != "":
    testsound = cfg["testsound"]
# end load config


pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

############
def play(audiofile):
    if pygame.mixer.music.get_busy():
        return

    if not audiofile.startswith('/'):
        audiofile = sounddir + audiofile

    # TODO: if its a URL, download it (unless we already have it)

    try:
        pygame.mixer.music.load(audiofile)
        pygame.mixer.music.play()
    except:
        print("Failed to play %s" % audiofile)

############
def on_disconnect(client, userdata,rc=0):
    print("DisConnected result code "+str(rc))
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
    elif mqtt.topic_matches_sub("follyengine/"+myHostname+"/play", message.topic):
        print(myHostname+" plays "+payload)
        play(payload)

########################################

client = mqtt.Client(myHostname+"_audio") #create new instance
client.on_message=on_message #attach function to callback
client.on_disconnect=on_disconnect

print("Connecting to MQTT at: %s" % mqttHost)
client.connect(mqttHost) #connect to broker

client.subscribe("follyengine/"+myHostname+"/play")
client.subscribe("follyengine/+/test")

client.publish("status/"+myHostname+"/audio","STARTED")

play(testsound)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exit")

client.publish("status/"+myHostname+"/audio","STOPPED")
