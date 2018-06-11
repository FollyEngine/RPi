
from __future__ import print_function
from time import sleep

import sys

import smartcard.System

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import CardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
from smartcard.CardConnection import CardConnection

from threading import Event

# start pcscd daemon
from subprocess import call

import paho.mqtt.publish as publish
import json
import socket

GETUID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
mqttHost = "10.10.11.2"
myHostname = socket.gethostname()

# a simple card observer that prints inserted/removed cards
class PrintObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("+Inserted: ", toHexString(card.atr))

            try:
                connection = card.createConnection()
                connection.connect( CardConnection.T1_protocol )
                response, sw1, sw2 = connection.transmit(GETUID)
                #print ('response: ', response, ' status words: ', "%x %x" % (sw1, sw2))
                tagid = toHexString(response).replace(' ','')
                print ("tagid ",tagid)
    
                #payload = json.dumps({
                #        'id': 'one',
                #        'tag': tagid,
                #        'event': 'inserted'
                #    });
                #publish.single("realengine/rfid/inserted", payload, hostname=mqttHost)
                publish.single("realengine/"+myHostname+"/rfid", tagid, hostname=mqttHost)
            except:
                print("ERROR")


        for card in removedcards:
            print("-Removed:  ", toHexString(card.atr))

            publish.single("realengine/"+myHostname+"/rfid", "REMOVED", hostname=mqttHost)


###########################################
if __name__ == '__main__':

    if len(sys.argv) > 1:
        mqttHost = sys.argv[1]

    print("Connecting to MQTT at: %s" % mqttHost)

    call(['/usr/sbin/pcscd'])
    # TODO: detect if there isn't a reader pluigged in, and exit...
    readers = smartcard.System.readers()
    sleep(1)
    if len(readers) < 1:
        print("No RFID readers found, EXITING")
        exit()

    print(readers)

    print("Waiting for smartcard or RFID.")
    print("")
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver()
    cardmonitor.addObserver(cardobserver)

    publish.single("status/"+myHostname+"/rfid", "listening", hostname=mqttHost)

    while True:
        cardtype = AnyCardType()
        cardrequest = CardRequest(timeout=10, cardType=cardtype)
        try:
            cardservice = cardrequest.waitforcard()

        except CardRequestTimeoutException:
            print("retry:")
           
        except KeyboardInterrupt:
			print("exit")
			sys.exit()

    # don't forget to remove observer, or the
    # monitor will poll forever...
    cardmonitor.deleteObserver(cardobserver)

    import sys
    if 'win32' == sys.platform:
        print('press Enter to continue')
        sys.stdin.read(1)
