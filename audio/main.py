import paho.mqtt.client as mqtt #import the client1
import time
import sys
from subprocess import call

host="hostname"

############
def on_message(client, userdata, message):
    payload=str(message.payload.decode("utf-8"))
    print("")
    print("message received " ,payload)
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    if mqtt.topic_matches_sub("play/all", message.topic):
        # everyone
        call(['/usr/bin/paplay', payload])
    elif mqtt.topic_matches_sub("play/test", message.topic):
        call(['/usr/bin/paplay', 'test.wav'])
    elif mqtt.topic_matches_sub("play/"+host, message.topic):
        call(['/usr/bin/paplay', payload])

########################################
broker_address="mqs_server"
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker

client.subscribe("#")
client.publish("status/"+host+"/audio","STARTED")

while True:
    try:
        client.loop()
    except KeyboardInterrupt:
        print("exit")
        sys.exit()

client.publish("status/"+host+"/audio","STOPPED")
