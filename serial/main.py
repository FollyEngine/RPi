#!/usr/bin/python3

#OMG https://lo.calho.st/projects/the-fruits-of-some-recent-arduino-mischief/

import serial
from time import sleep

#ser = serial.Serial('/dev/ttyUSB0')
#print(ser.name)

def readreply():
    packet_type = ser.read(1)
    p = int.from_bytes(packet_type, byteorder="big")
    if p != 0:
        print("type == %s" % format(p, '#04x'))

        l = ser.read(1)
        length = int.from_bytes(l, byteorder="big")
        print("length == %u" % length)

        if length > 0:
            data = ser.read(length)
            d = int.from_bytes(data, byteorder="big")
            print("data == %s" % format(d, '#04x'))


with serial.Serial('/dev/ttyUSB1', 9600, timeout=10) as ser:
    #try:
        # get version
        ser.write(b'\xA0\x03\x6A\x00\xF3')
        header = ser.read(3)
        usercode = ser.read(1)
        ver = ser.read(2)
        checksum = ser.read(1)
        print(ver)


        # close beep sound when reading a tag?
        #ser.write(b'\xA0\x04\xB0\x00\x00\xAC')
        #sleep(1)
        #        readreply()

        # open beep sound when reading a tag
        #ser.write(b'\xA0\x04\xB0\x00\x01\xAB')
        #sleep(1)
        #readreply()

        # sound beep once
        ser.write(b'\xA0\x04\xB0\x00\x02\xAA')
        sleep(1)
        readreply()

        ser.write(b'\xA0\x04\xB0\x00\x02\xAA')
        sleep(1)
        readreply()

        # reset command frames
        ser.write(b'\xA0\x03\x65\x00\xF8')
        sleep(1)
        readreply()

        # restart tag identification function
        ser.write(b'\xA0\x03\xFC\x00\x61')
        sleep(1)
        readreply()

        while True:
            try:
                id = ser.read(17)
            except serial.serialutil.SerialException:
                continue
            tagid = int.from_bytes(id, byteorder="big")
            if tagid == 0:
                print("nope")
            else:
                print("tag1 == %s" % format(tagid, '#04x'))


        while True:
            start = ser.read(2) # 0x00

            id = ser.read(12)
            tagid = int.from_bytes(id, byteorder="big")
            print("tag2 == %s" % format(tagid, '#04x'))
            sep = ser.read(1)
            crc = ser.read(1)
            trail = ser.read(1)


        #x = ser.read()          # read one byte
        #s = ser.read(10)        # read up to ten bytes (timeout)
        #line = ser.readline()

        print(ser.name)
    #except:
    #    ser.close()

        #print("%o: %u, %o, %o" % (packet_type, length, code, devicenumber))
        #print("%s: %s, %s, %s" % (packet_type, length, code, devicenumber))
