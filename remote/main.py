#!/usr/bin/python

from __future__ import print_function
from time import sleep

import struct
import time
import sys

import paho.mqtt.publish as publish
import socket
import yaml

#######
# load config (extract to lib)
configFile = "config.yml"
if len(sys.argv) > 1:
    configFile = sys.argv[1]

if len(sys.argv) > 2:
    infile_path = sys.argv[2] 
else:
    infile_path = "/dev/input/by-id/usb-AleTV_Remote_V1_RF_USB_Controller-if01-event-kbd"


with open(configFile, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

mqttHost = "mqtt"
if "mqtthostname" in cfg and cfg["mqtthostname"] != "":
    mqttHost = cfg["mqtthostname"]

myHostname = socket.gethostname()
if "hostname" in cfg and cfg["hostname"] != "":
    myHostname = cfg["hostname"]

sounddir = '/mnt/'
testsound='test.wav'
# end load config

############
keys = {
    # /dev/input/by-id/usb-AleTV_Remote_V1_RF_USB_Controller-if01-event-kbd
    272: 'OK',
    273: 'mouse_right_button',
    # /dev/input/by-id/usb-AleTV_Remote_V1_RF_USB_Controller-if01-event-kbd
    28: 'OK',
    103: 'up_arrow',
    108: 'down_arrow',
    106: 'right_arrow',
    105: 'left_arrow',
    114: 'volume_down',
    115: 'volume_up',
    172: 'home',
    127: 'menu',
    1: 'back',
    113: 'mute',
    217: 'search',
    165: 'rewind',
    163: 'fast_forward',
    142: 'off'
}



###########################################
if __name__ == '__main__':
    print("Connecting to MQTT at: %s" % mqttHost)

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode
in_file = open(infile_path, "rb")

event = in_file.read(EVENT_SIZE)

while event:
    # https://www.kernel.org/doc/Documentation/input/input.txt
    (tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)

    # Events with code, type and value == 0 are "separator" events
    if value == 0 and code != 0:
        # keyup
        #print("Event type %u, code %u, value %u at %d.%d" % \
        #    (type, code, value, tv_sec, tv_usec))
        print("code %u" % (code))
        key = "code %u" % (code)
        if code in keys:
            key = keys[code]
        publish.single("follyengine/"+myHostname+"/remote", key, hostname=mqttHost)

    try:
        event = in_file.read(EVENT_SIZE)

    except KeyboardInterrupt:
        print("exit")
        break

if 'win32' == sys.platform:
    print('press Enter to continue')
    sys.stdin.read(1)

in_file.close()
