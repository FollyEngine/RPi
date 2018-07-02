import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
#from subprocess import call
import yaml

allMuted = False
repeats["sven"] = 1

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

# end load config

############
def muteAll():
   publish.single("follyengine/all/mute", "", hostname=mqttHost)

############
def unMuteAll():
   publish.single("follyengine/all/unmute", "", hostname=mqttHost)

############
def unMute(host):
   publish.single("follyengine/"+host+"/unmute", "", hostname=mqttHost)

############
def play(audiofile):
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
    print(message.topic+": "+payload)

    #print("message received " ,payload)
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
    if mqtt.topic_matches_sub("follyengine/all/rfid", message.topic):
        currentState = payload
        return

    try:
        if mqtt.topic_matches_sub("follyengine/all/rfid", message.topic) or mqtt.topic_matches_sub("follyengine/"+myHostname+"/rfid", message.topic):
            item = cfg["items"][payload]
            print(myHostname+" got "+payload+" which is: "+item)

            if item == "mute":
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
                print("heros: ")
                if currentState == myHostname and myHostname in cfg["heros"]:
                    heroItem = cfg["heros"][myHostname]["item"]
                    print("podium "+myHostname+" hero is '"+heroItem+"' got '"+item+"'")
                    if item == heroItem:
                        print("got hero item "+item+" playing its hero speach")
                        item = "hero"
                        currentState = cfg["heros"][myHostname]["next"]
                        state(currentState)
                        # if we're the hero item on the right podium, quiet everyone else!
                        #muteAll()
                        #unMute(myHostname)
                        #sleepMs(500)

            if item in repeats:
                if repeats[item] == 1:
                    item = "No_A"
                elif repeats[item] == 1:
                    item = "No_B"
                else:
                    item = "No_C"
                repeats[item] = 1 + repeats[item]
            else
                repeats[item] = 1

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


            play(audiofile)
            
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

client.subscribe("follyengine/"+myHostname+"/rfid")
client.subscribe("follyengine/all/state")

client.publish("status/"+myHostname+"/controller","STARTED")
publish.single("follyengine/"+myHostname+"/test", "test", hostname=mqttHost)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exit")

client.publish("status/"+myHostname+"/controller","STOPPED")
