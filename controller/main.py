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

############
def on_message(client, userdata, message):
    global allMuted
    global currentState
    global repeats

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
        if hostmqtt.topic_matches_sub("all/state/set", message.topic):
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
            return
        if hostmqtt.topic_matches_sub(myHostname+"/audio/played", message.topic):
            sound = payload["sound"]
            if sound == config.cfg["podium"][myHostname]["hero"]:
                unMuteAll()
                state(config.cfg["heros"][myHostname]["next"])
            return
        if hostmqtt.topic_matches_sub(myHostname+"/remote/scan", message.topic):
            item = payload["item"]
            play(item)
            return
        if hostmqtt.topic_matches_sub(myHostname+"/rfid-nfc/scan", message.topic):
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

    except Exception as e:
        print("Exception:")
        traceback.print_exc()
        return
########################################

# TODO: I'd like to make this implicit
hostmqtt.set_on_message(on_message)


hostmqtt.subscribeL(myHostname, "remote", "scan")
hostmqtt.subscribeL(myHostname, "rfid-nfc", "scan")
hostmqtt.subscribeL(myHostname, "rfid-nfc", "removed")
hostmqtt.subscribeL(myHostname, "audio", "played")
hostmqtt.subscribeL("all", "state", "set")

hostmqtt.publish("status", {"status": "listening"})

state(config.cfg["start_state"])

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.publish("status",{"status": "STOPPED"})
