#!/usr/bin/python3

#OMG https://lo.calho.st/projects/the-fruits-of-some-recent-arduino-mischief/

import serial
from time import sleep

#ser = serial.Serial('/dev/ttyUSB0')
#print(ser.name)

with serial.Serial('/dev/ttyUSB1', 9600, timeout=1) as ser:
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

        # open beep sound when reading a tag
        #ser.write(b'\xA0\x04\xB0\x00\x01\xAB')
        #sleep(1)

        # sound beep once
        ser.write(b'\xA0\x04\xB0\x00\x02\xAA')
        sleep(1)
        ser.write(b'\xA0\x04\xB0\x00\x02\xAA')
        sleep(1)
        ser.write(b'\xA0\x04\xB0\x00\x02\xAA')
        sleep(1)


        #x = ser.read()          # read one byte
        #s = ser.read(10)        # read up to ten bytes (timeout)
        #line = ser.readline()

        print(ser.name)
        while True:
            #data = ser.read(999)
            #b = bin(int.from_bytes(data, byteorder="big")).strip('0b')
            #print(b)

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
            else:
                sleep(0.2)
                #print("timeout")
    #except:
    #    ser.close()

        #print("%o: %u, %o, %o" % (packet_type, length, code, devicenumber))
        #print("%s: %s, %s, %s" % (packet_type, length, code, devicenumber))
