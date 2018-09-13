import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
#from subprocess import call
import yaml

allMuted = False
repeats = {}

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

currentState = "PodiumX"
if "start_state" in cfg and cfg["start_state"] != "":
    currentState = cfg["start_state"]

print(cfg["heros"][currentState])
# end load config

############
def muteAll():
    publish.single("follyengine/all/mute", "", hostname=mqttHost)

############
def unMuteAll():
    publish.single("follyengine/all/unmute", "", hostname=mqttHost)

############
def unMute(host):
    publish.single("follyengine/"+host+"/unmute", host, hostname=mqttHost)

############
def play(item):
    audiofile = ""
    if "podium" in cfg:
        if "default" in cfg["podium"]:
            if "(null)" in cfg["podium"]["default"]:
                audiofile = cfg["podium"]["default"]["(null)"]
        if "default" in cfg["podium"]:
            if item in cfg["podium"]["default"]:
                audiofile = cfg["podium"]["default"][item]
        if myHostname in cfg["podium"]:
            if item in cfg["podium"][myHostname]:
                audiofile = cfg["podium"][myHostname][item]

    publish.single("follyengine/"+myHostname+"/play", audiofile, hostname=mqttHost)

############
def state(nextState):
    publish.single("follyengine/all/state", nextState, hostname=mqttHost)


############
def on_message(client, userdata, message):
    global allMuted
    global currentState
    global repeats

    payload=str(message.payload.decode("utf-8"))
    if payload == "" or payload == "REMOVED" or payload == "(null)":
        return

    print(message.topic+": "+payload)

    #print("message received " ,payload)
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
    if mqtt.topic_matches_sub("follyengine/all/state", message.topic):
        if payload == "reset":
            currentState = cfg["start_state"]
            repeats.clear()
            play("reset")
            return
        previousState = currentState
        print("Changing state from "+currentState+" to "+payload)
        currentState = payload

        if currentState == "FutureText":
            play("future")
        elif currentState == "ButNotForUs":
            play("butnotforus")
        else:
            if previousState == myHostname:
                # only play the state transition twinkle on the just hero'd podium
                unMute(myHostname)
                play("next_state")
        return
    if mqtt.topic_matches_sub("status/"+myHostname+"/played", message.topic):
        if payload == cfg["podium"][myHostname]["hero"]:
            unMuteAll()
            state(cfg["heros"][myHostname]["next"])
        return
    if mqtt.topic_matches_sub("follyengine/"+myHostname+"/remote", message.topic):
        play(payload)
        return
    try:
        if mqtt.topic_matches_sub("follyengine/all/rfid", message.topic) or mqtt.topic_matches_sub("follyengine/"+myHostname+"/rfid", message.topic):
            # TODO: this needs re-writing to only convert from rfid tag to item, post to MQ
            # TODO: and then another even listens to item values on the MQ and converts to action
            item = cfg["items"][payload]
            print(myHostname+" got "+payload+" which is: "+item)

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

            if "heros" in cfg:
                print("hero for: "+myHostname)

                if myHostname in cfg["heros"]:
                    print(cfg["heros"][myHostname])
                    heroItem = cfg["heros"][myHostname]["item"]
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
            if "allowrepeats" in cfg:
                if item in cfg["allowrepeats"]:
                    # don't do the no-repeat stuff here
                    play(item)
                    return

            if item in repeats:
                repeats[item] = 1 + repeats[item]
                client.publish("repeat/"+myHostname+"/"+item, repeats[item])

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
            if "sparkles" in cfg:
                if item == cfg["sparkles"]:
                    client.publish("follyengine/"+myHostname+"/neopixel", item)

    except Exception as e:
        print("Exception:")
        print(e)
        return
########################################

client = mqtt.Client(myHostname+"_controller") #create new instance
client.on_message=on_message #attach function to callback

print("Connecting to MQTT at: %s" % mqttHost)
client.connect(mqttHost) #connect to broker

client.subscribe("follyengine/"+myHostname+"/remote")
client.subscribe("follyengine/"+myHostname+"/rfid")
client.subscribe("status/"+myHostname+"/played")  # used for hero mute and state

client.subscribe("follyengine/all/state")

client.publish("status/"+myHostname+"/controller","STARTED")
publish.single("follyengine/"+myHostname+"/test", "test", hostname=mqttHost)
state(cfg["start_state"])

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exit")

client.publish("status/"+myHostname+"/controller","STOPPED")
