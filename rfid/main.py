
from __future__ import print_function
from time import sleep

import smartcard.System

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import CardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException

from threading import Event

# start pcscd daemon
from subprocess import call

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
        for card in removedcards:
            print("-Removed:  ", toHexString(card.atr))



###########################################
if __name__ == '__main__':
    call(['pcscd'])
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

    while True:
        cardtype = AnyCardType()
        cardrequest = CardRequest(timeout=10, cardType=cardtype)
        try:
            cardservice = cardrequest.waitforcard()
        except CardRequestTimeoutException:
            print("retry:")


    # don't forget to remove observer, or the
    # monitor will poll forever...
    cardmonitor.deleteObserver(cardobserver)

    import sys
    if 'win32' == sys.platform:
        print('press Enter to continue')
        sys.stdin.read(1)