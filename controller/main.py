#!//usr/bin/python3

import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
import traceback

allMuted = False
repeats = {}


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./rfid/')
import mqtt
import config

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "controller")

currentState = "NEWNEWNEW" #config.getValue("start_state", "PodiumX")

# end load config

############
def muteAll():
    hostmqtt.publishL("all", "audio", "mute", {})

############
def unMuteAll():
    hostmqtt.publishL("all", "audio", "unmute", {})

############
def unMute(host):
    hostmqtt.publishL(host, "audio", "mute", {})

############
def play(item):
    audiofile = ""
    if "podium" in config.cfg:
        if "default" in config.cfg["podium"]:
            if "(null)" in config.cfg["podium"]["default"]:
                audiofile = config.cfg["podium"]["default"]["(null)"]
        if "default" in config.cfg["podium"]:
            if item in config.cfg["podium"]["default"]:
                audiofile = config.cfg["podium"]["default"][item]
        if myHostname in config.cfg["podium"]:
            if item in config.cfg["podium"][myHostname]:
                audiofile = config.cfg["podium"][myHostname][item]

    hostmqtt.publishL(myHostname, "audio", "play", {"sound": audiofile})


############
def state(nextState):
    hostmqtt.publishL("all", "state", "set", {"state": nextState})

########################################################
# subscription handlers
def msg_state_set(topic, payload):
    global currentState

    nextState = payload["state"]
    if nextState == "reset":
        currentState = config.cfg["start_state"]
        repeats.clear()
        play("reset")
        return
    previousState = currentState
    print("Changing state from "+currentState+" to "+nextState)
    currentState = nextState
    if previousState == "NEWNEWNEW":
        unMuteAll()
    elif currentState == "FutureText":
        play("future")
    elif currentState == "ButNotForUs":
        play("butnotforus")
    else:
        if previousState == myHostname:
            # only play the state transition twinkle on the just hero'd podium
            unMute(myHostname)
            play("next_state")

def msg_audio_played(topic, payload):
    sound = payload["sound"]
    if sound == config.cfg["podium"][myHostname]["hero"]:
        unMuteAll()
        state(config.cfg["heros"][myHostname]["next"])

def msg_remote_scan(topic, payload):
    play(payload["item"])

def msg_rfid_scan(topic, payload):
    # TODO: this needs re-writing to only convert from rfid tag to item, post to MQ
    # TODO: and then another even listens to item values on the MQ and converts to action
    tag = payload["tag"]
    item = config.cfg["items"][tag]
    print(myHostname+" got "+tag+" which is: "+item)

    if item == "reset":
        state("reset")
        return
    elif item == "mute":
        print("-----------------------")
        if allMuted:
            print("unMute all")
            unMuteAll()
            allMuted = False
        else:
            print("Mute all")
            muteAll()
            allMuted = True
        return

    if "heros" in config.cfg:
        print("hero for: "+myHostname)

        if myHostname in config.cfg["heros"]:
            print(config.cfg["heros"][myHostname])
            heroItem = config.cfg["heros"][myHostname]["item"]
            print("podium "+myHostname+" hero is '"+heroItem+"' got '"+item+"'")
            if item == "playhero":
                #play the hero speech without changing the state
                item = heroItem
                print("forcing hero item "+item+" playing its hero speech")
                if currentState == myHostname:
                    # if this podium is the currentstate, advance the state too
                    play("hero")
                else:
                    #otherwise, play the non-twinkly hero
                    play(item)

                return
            elif item == heroItem:
                # this podium's hero item was placed
                if currentState == myHostname:
                    # its this podium's turn to succeed!
                    print("got hero item "+item+" playing its hero speech")
                    # tell everyone to go to the next podium
                    # if we're the hero item on the right podium, quiet everyone else!
                    muteAll()
                    unMute(myHostname)
                    #sleepMs(500)
                    play("hero")
                    # the "finished playing signal" from audio will trigger the unmute and state transition
                    return
                else:
                    # its not this podium's turn, so we read the non-hero text
                    item = "hero_no"

    #if item == "sven" or item == "twinkle" or item == "letter", sweet, sour, salty
    if "allowrepeats" in config.cfg:
        if item in config.cfg["allowrepeats"]:
            # don't do the no-repeat stuff here
            play(item)
            return

    if item in repeats:
        repeats[item] = 1 + repeats[item]
        # not subscribed to atm
        hostmqtt.publish("repeat", {"item": item, "repeat": repeats[item]})

        if repeats[item] == 1:
            item = "No_A"
        elif repeats[item] == 2:
            item = "No_B"
        else:
            item = "No_C"
    else:
        repeats[item] = 0

    play(item)
    
    # neopixels
    if "sparkles" in config.cfg:
        if item == config.cfg["sparkles"]:
            hostmqtt.publish("neopixel", {"item": item})

########################################

hostmqtt.subscribeL(myHostname, "remote", "scan", msg_remote_scan)
hostmqtt.subscribeL(myHostname, "rfid-nfc", "scan", msg_rfid_scan)
#hostmqtt.subscribeL(myHostname, "rfid-nfc", "removed")
hostmqtt.subscribeL(myHostname, "audio", "played", msg_audio_played)
hostmqtt.subscribeL("all", "state", "set", msg_state_set)

hostmqtt.publish("status", {"status": "listening"})

state(config.cfg["start_state"])

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.publish("status",{"status": "STOPPED"})
