#!/usr/bin/python3

import time
import sys
import socket
import logging

# for midi generation
from pyo import *
import random


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
hostmqtt.loop_start()   # use the background thread

sounddir = config.getValue("sounddir", "../../sounds/")
testsound = config.getValue("testsound", "test.wav")

isMuted = False  

def main():
    s = Server(duplex=0)
    s.setOutputDevice(pa_get_default_output())
    s.boot()
    s.start()
    time.sleep(1)

    # sf = SfPlayer("./audio/test.wav", speed=1, loop=False).out()
    # time.sleep(3)
    # print("ready")

    # a = Sine(mul=0.01).out()
    # time.sleep(1)

    # midiplay()
    # time.sleep(0.0001)
    # midiplay()
    # time.sleep(0.0001)
    # midiplay()
    # time.sleep(0.0001)
    # click_sound = Fader(dur=0.01, mul=1)
    # a = FastSine(mul=click_sound).mix(2).out()
    # click_sound.play()
    # time.sleep(0.1)
    # #sf = SfPlayer("./audio/test.wav", speed=1, loop=False).out()

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
        # hostmqtt.loop_forever()
        clicker_loop()
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
    # if pygame.mixer.music.get_busy():
    #     logging.info("audio mixer is busy")
    #     return

    audioPath = audiofile
    if not audioPath.startswith('/'):
        audioPath = sounddir + audioPath

    # TODO: if its a URL, download it (unless we already have it)

    try:
        sf = SfPlayer(audioPath, speed=1, loop=True).out()
        (frames, seconds, rate, channels, format, type) = sndinfo(audioPath)
        time.sleep(seconds)
        # pygame.mixer.music.load(audioPath)
        # pygame.mixer.music.play()
        # while pygame.mixer.music.get_busy():
        #     pygame.time.Clock().tick(10)
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
    #pygame.mixer.fadeout(100)


def msg_unmute(topic, payload):
    global isMuted
    isMuted = False
    logging.info("unmuted")


clickchance=0
clickchange_set_time=0
decay=8
def clicker_loop():
    global clickchance, clickchange_set_time
    clicks=0
    loops=0
    max = 100 ** decay
    while True:
        loops = loops+1
        r = random.randint(1,max+1)
        if r <= clickchance:
            clicks = clicks+1
            midiplay()
        if clickchance > 0:
            if (clickchange_set_time + 100) < (time.time_ns() // 1000000):
                logging.debug("clicked %d/%d (%d/%d)" % (clicks, loops, clickchance, max))
                clickchance = 0
                clicks=0
                loops=0


# for the void-detector
# the yellow rfid reader takes ~120ms between reads
# the rssi from the square takes seems to go between 50 and 100
# so what if we use 2*(rssi-50) as how many clicks we should hear in the next 120ms
def msg_midi(topic, payload):
    global clickchance, clickchange_set_time
    rssi = mqtt.get(payload, "rssi", 100)
    clickchance = 2*(rssi-50)
    clickchance = clickchance ** decay
    clickchange_set_time = time.time_ns() // 1000000
    #logging.debug("chance: %d / 100" % clickchance)

# click_sound = 0
def midiplay(duration = 0.001, volume=1):
    # global click_sound
    # if click_sound == 0:
    click_sound = Fader(dur=duration, mul=volume)
    a = FastSine(mul=click_sound).mix(2).out()
    click_sound.play()
    time.sleep(0.001)


########################################
if __name__=="__main__":
   main()