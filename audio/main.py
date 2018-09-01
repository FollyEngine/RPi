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

# TODO: fix this...
# 100% CPU load using pygame:
# https://github.com/pygame/pygame/issues/331
pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

isMuted = False

############
def play(audiofile):
    if isMuted:
        print(myHostname+" is muted, not playing "+audiofile)
        return
    # if we're already playing something then ignore new play command
    if pygame.mixer.music.get_busy():
        return

    audioPath = audiofile
    if not audioPath.startswith('/'):
        audioPath = sounddir + audioPath

    # TODO: if its a URL, download it (unless we already have it)

    try:
        pygame.mixer.music.load(audioPath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        client.publish("status/"+myHostname+"/played",audiofile)
    except Exception as e:
        print("Failed to play %s" % audioPath)
        print("Exception:")
        print(e)


############
def on_disconnect(client, userdata,rc=0):
    print("DisConnected result code "+str(rc))
    #client.loop_stop()

############
def on_message(client, userdata, message):
    global isMuted
    payload=str(message.payload.decode("utf-8"))
    print(message.topic+": "+payload)
    #print("message received " ,payload)
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
    if mqtt.topic_matches_sub("follyengine/all/play", message.topic) and payload != "":
        # everyone
        print("everyone plays "+payload)
        play(payload)
    elif mqtt.topic_matches_sub("follyengine/all/test", message.topic):
        print("everyone plays test.wav")
        play(testsound)
    elif mqtt.topic_matches_sub("follyengine/"+myHostname+"/play", message.topic) and payload != "":
        print(myHostname+" plays "+payload)
        play(payload)
    elif mqtt.topic_matches_sub("follyengine/all/mute", message.topic) or mqtt.topic_matches_sub("follyengine/"+myHostname+"/mute", message.topic):
        isMuted = True
        print("muted")
        # podiums stop making sounds
        pygame.mixer.fadeout(100)
        # TODO: add an exception for the hero podium...
    elif mqtt.topic_matches_sub("follyengine/all/unmute", message.topic) or mqtt.topic_matches_sub("follyengine/"+myHostname+"/unmute", message.topic):
        # podiums can make sounds
        isMuted = False
        print("unmuted")

########################################

client = mqtt.Client(myHostname+"_audio") #create new instance
client.on_message=on_message #attach function to callback
client.on_disconnect=on_disconnect

print("Connecting to MQTT at: %s" % mqttHost)
client.connect(mqttHost) #connect to broker

client.subscribe("follyengine/"+myHostname+"/play")
client.subscribe("follyengine/"+myHostname+"/unmute")
client.subscribe("follyengine/+/test")
client.subscribe("follyengine/all/+")

client.publish("status/"+myHostname+"/audio","STARTED")

play(testsound)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exit")

client.publish("status/"+myHostname+"/audio","STOPPED")
