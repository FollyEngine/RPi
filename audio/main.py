#!/usr/bin/python3

import time
import sys
import socket
import pygame
import logging

# for midi generation
import math
import numpy


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt

myHostname = config.getHostname()
deploymenttype=config.getDeploymentType()
DEVICENAME=config.getDevicename()

mqttHost = config.getValue("mqtthostname", "localhost")
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
#hostmqtt.loop_start()   # use the background thread

sounddir = config.getValue("sounddir", "../../sounds/")
testsound = config.getValue("testsound", "test.wav")

# TODO: fix this...
# 100% CPU load using pygame:
# https://github.com/pygame/pygame/issues/331
pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

isMuted = False  

def main():
    midiplay()

    hostmqtt.subscribe("mute", msg_mute)
    hostmqtt.subscribeL("all", DEVICENAME, "mute", msg_mute)
    hostmqtt.subscribe("unmute", msg_unmute)
    hostmqtt.subscribeL("all", DEVICENAME, "unmute", msg_unmute)

    hostmqtt.subscribe("play", msg_play)
    hostmqtt.subscribeL("all", DEVICENAME, "play", msg_play)

    hostmqtt.subscribe("midi", msg_midi)
    hostmqtt.subscribeL("all", DEVICENAME, "midi", msg_midi)

    hostmqtt.subscribe("test", msg_test)
    hostmqtt.subscribeL("all", DEVICENAME, "test", msg_test)

    hostmqtt.status({"status": "listening"})

    # trigger a play...
    play(testsound)

    try:
        #while True:
        #    time.sleep(1)
        hostmqtt.loop_forever()
    except Exception as ex:
        logging.error("Exception occurred", exc_info=True)
    except KeyboardInterrupt:
        logging.info("exit")

    hostmqtt.status({"status": "STOPPED"})

############
def play(audiofile):
    if isMuted:
        logging.info(myHostname+" is muted, not playing "+audiofile)
        return
    # if we're already playing something then ignore new play command
    if pygame.mixer.music.get_busy():
        logging.info("audio mixer is busy")
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
        logging.info("played %s" % audioPath)
    except Exception as e:
        logging.info("Failed to play %s" % audioPath)
        logging.error("Exception occurred", exc_info=True)

########################################
# on_message subscription functions
def msg_play(topic, payload):
    sound = payload["sound"]
    logging.info("everyone plays "+sound)
    play(sound)



def msg_test(topic, payload):
    logging.info("everyone plays test.wav")
    play(testsound)

def msg_mute(topic, payload):
    global isMuted
    isMuted = True
    logging.info("muted")
    pygame.mixer.fadeout(100)


def msg_unmute(topic, payload):
    global isMuted
    isMuted = False
    logging.info("unmuted")

def msg_midi(topic, payload):
    midiplay()

def midiplay(duration = 0.0005, frequency_l = 440, frequency_r = 550):
    bits = 16
    ## Really show duration gext us a click
    duration = 0.0005         # in seconds
    #freqency for the left speaker
    frequency_l = 440
    #frequency for the right speaker
    frequency_r = 550

    #this sounds totally different coming out of a laptop versus coming out of headphones

    sample_rate = 44100

    n_samples = int(round(duration*sample_rate))

    #setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
    buf = numpy.zeros((n_samples, 2), dtype = numpy.int16)
    max_sample = 2**(bits - 1) - 1

    for s in range(n_samples):
        t = float(s)/sample_rate    # time in seconds

        #grab the x-coordinate of the sine wave at a given time, while constraining the sample to what our mixer is set to with "bits"
        buf[s][0] = int(round(max_sample*math.sin(2*math.pi*frequency_l*t)))        # left
        buf[s][1] = int(round(max_sample*0.5*math.sin(2*math.pi*frequency_r*t)))    # right

    sound = pygame.sndarray.make_sound(buf)
    #play once,  (-1 loops forever)
    sound.play(loops = 1)


########################################
if __name__=="__main__":
   main()