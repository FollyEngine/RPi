#!/usr/bin/python3

import time
import sys
import socket
import pygame
import traceback

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./rfid/')
import config
import mqtt

DEVICENAME="audio"

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

sounddir = config.getValue("sounddir", "/mnt/")
testsound = config.getValue("testsound", "test.wav")

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
        hostmqtt.publish("played", {"status": "played", "sound": audiofile})
    except Exception as e:
        print("Failed to play %s" % audioPath)
        traceback.print_exc()

############
def on_message(client, userdata, message):
    global isMuted

    try:
        raw_payload=str(message.payload.decode("utf-8"))
        print("RAW: "+message.topic+": "+raw_payload)
        if raw_payload == "" or raw_payload == "REMOVED" or raw_payload == "(null)":
            return

        payload = hostmqtt.decode(raw_payload)
        print("DECODED: "+message.topic+": "+str(payload))
        #print("message received " ,payload)
        #print("message topic=",message.topic)
        #print("message qos=",message.qos)
        #print("message retain flag=",message.retain)

        if hostmqtt.topic_matches_sub("all/audio/play", message.topic) and payload != "":
            # everyone
            sound = payload["sound"]
            print("everyone plays "+sound)
            play(sound)
        elif hostmqtt.topic_matches_sub("all/audio/test", message.topic):
            print("everyone plays test.wav")
            play(testsound)
        elif hostmqtt.topic_matches_sub(myHostname+"/audio/play", message.topic) and payload != "":
            sound = payload["sound"]
            print(myHostname+" plays "+sound)
            play(sound)
        elif hostmqtt.topic_matches_sub("all/audio/mute", message.topic) or hostmqtt.topic_matches_sub(myHostname+"/audio/mute", message.topic):
            isMuted = True
            print("muted")
            # podiums stop making sounds
            pygame.mixer.fadeout(100)
            # TODO: add an exception for the hero podium...
        elif hostmqtt.topic_matches_sub("all/audio/unmute", message.topic) or hostmqtt.topic_matches_sub(myHostname+"/audio/unmute", message.topic):
            # podiums can make sounds
            isMuted = False
            print("unmuted")
    except Exception as e:
        traceback.print_exc()

########################################

# TODO: I'd like to make this implicit
hostmqtt.set_on_message(on_message)

hostmqtt.subscribe("play")
hostmqtt.subscribe("mute")
hostmqtt.subscribe("unmute")
hostmqtt.subscribe("test")
hostmqtt.subscribeL("all", DEVICENAME, "test")
hostmqtt.subscribeL("all", DEVICENAME, "play")
hostmqtt.subscribeL("all", DEVICENAME, "mute")
hostmqtt.subscribeL("all", DEVICENAME, "unmute")

hostmqtt.publish("status", {"status": "listening"})

play(testsound)

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.publish("status",{"status": "STOPPED"})
