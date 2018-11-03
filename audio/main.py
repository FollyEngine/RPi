#!/usr/bin/python3

import time
import sys
import socket
import pygame


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./rfid/')
import config
import mqtt

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "audio")

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
        print("Exception:")
        print(e)

############
def on_message(client, userdata, message):
    global isMuted
    payload=str(message.payload.decode("utf-8"))
    print(message.topic+": "+payload)
    #print("message received " ,payload)
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
    try:
        if hostmqtt.topic_matches_sub("follyengine/all/play", message.topic) and payload != "":
            # everyone
            print("everyone plays "+payload)
            play(payload)
        elif hostmqtt.topic_matches_sub("follyengine/all/test", message.topic):
            print("everyone plays test.wav")
            play(testsound)
        elif hostmqtt.topic_matches_sub("follyengine/"+mqtt_host_device+"/play", message.topic) and payload != "":
            print(myHostname+" plays "+payload)
            play(payload)
        elif hostmqtt.topic_matches_sub("follyengine/all/mute", message.topic) or hostmqtt.topic_matches_sub("follyengine/"+myHostname+"/mute", message.topic):
            isMuted = True
            print("muted")
            # podiums stop making sounds
            pygame.mixer.fadeout(100)
            # TODO: add an exception for the hero podium...
        elif hostmqtt.topic_matches_sub("follyengine/all/unmute", message.topic) or hostmqtt.topic_matches_sub("follyengine/"+myHostname+"/unmute", message.topic):
            # podiums can make sounds
            isMuted = False
            print("unmuted")
    except Exception as e:
        print("Exception:")
        print(e)

########################################

# TODO: I'd like to make this implicit
hostmqtt.set_on_message(on_message)

mqtt_host_device="%s_%s" % (myHostname, "rfid-nfc")
hostmqtt.subscribe("follyengine/"+mqtt_host_device+"/play")
hostmqtt.subscribe("follyengine/"+mqtt_host_device+"/unmute")
hostmqtt.subscribe("follyengine/+/test")
hostmqtt.subscribe("follyengine/all/+")

hostmqtt.publish("status", {"status": "listening"})

play(testsound)

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.publish("status",{"status": "STOPPED"})
