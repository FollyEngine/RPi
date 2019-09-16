#!/usr/bin/python3

import serial
from time import sleep
import socket
import logging

# for UHF RFID reader - the yellow one...
# D-10X

# docker run --rm -it --net host --device /dev/ttyUSB0 "follyengine"/rfid-d10x detect megagame rfid

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import mqtt
import config
import datetime

myHostname = config.getHostname()
deploymenttype=config.getDeploymentType()
DEVICENAME=config.getDevicename()

mqttHost = config.getValue("mqtthostname", "localhost")
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

# TODO: mode can be "trigger" (uses lastTimeRead),
#  "scan" - continuous insert messages for power-scanning,
#  "<specific tag EPC>" - continuous scanning, but only output power of the specified tag
MESSAGEMODE="scan"

global lastTimeRead
lastTimeRead = {}
########################################

def readreply(ser):
    p = ser.read(1)
    # assert(packet_type == 0xA0)
    packet_type = int.from_bytes(p, byteorder="big")
    #logging.info(packet_type)
    if packet_type != 0:
        #logging.info("type == %s" % format(packet_type, '#04x'))

        l = ser.read(1)
        length = int.from_bytes(l, byteorder="big")
        #logging.info("length == %u (0x%x)" % (length, length))

        if length > 0:
            a = ser.read(1)
            d = ser.read(length-2)
            c = ser.read(1)
            address = int.from_bytes(a, byteorder="big")
            data = int.from_bytes(d, byteorder="big")
            crc = int.from_bytes(c, byteorder="big")
            #logging.info("READ: type: %s, length: %d, address = %s data == %s" % (format(packet_type, '#04x'), length, format(address, '#04x'), format(data, '#04x')))

            return length, packet_type, data
    return 0, 0, "nothing"

def read_reply_real_time_inventory(ser):
    length, packet_type, data = readreply(ser_connection)
    if packet_type != 160:
        #big error
        return length, packet_type, data
    if len == 4:
        # failed to set to real time inventory
        throw# {"Error": "Failed to set to real time inventory"}
    if len == 10:
        #succeeded in reading a bunch
        # data contains read rate and total number read
        return length, packet_type, data
    hexData = "%x" % data #format(data, '#04x')
    FreqAnt = hexData[0:2]
    TagPC = hexData[2:4]
    EPC = hexData[4:-2]
    rssiStr = hexData[-2:]
    rssi = x = int(rssiStr, 16)

    publish = True
    if MESSAGEMODE == "trigger" and EPC in lastTimeRead:
        if lastTimeRead[EPC] != 0:
            publish = False # only send the message once - see expire in the main loop

    # not real tag reads
    if EPC == "":
        return length, packet_type, data
    elif EPC == "0000000000":
        return length, packet_type, data
    elif TagPC == "00":
        return length, packet_type, data

    if MESSAGEMODE == "trigger":
        # TODO: should filter these to not include the 00000000700000 type id's
        lastTimeRead[EPC] = datetime.datetime.now()
    elif MESSAGEMODE == "scan":
        publish = True
    else: # MESSAGEMODE == specific EPC, continuously publish it's rssi
        if MESSAGEMODE != EPC:
            publish = False


    if publish == True:
        sendInserted(MESSAGEMODE, EPC, FreqAnt, TagPC, rssi)

    return length, packet_type, data

def sendInserted(mode, EPC, FreqAnt, TagPC, rssi):
    event = {
        #'data': "%x" % data,
        #'packet_type': packet_type,
        "FreqAnt": FreqAnt,
        "TagPC": TagPC,
        "tag": EPC,
        "rssi": rssi,
        'event': 'inserted',
        'mode': mode
    }
    hostmqtt.publish("scan", event)


def sendRemoved(EPC, diff):
    event = {
        #'data': "%x" % data,
        #'packet_type': packet_type,
        #"FreqAnt": FreqAnt,
        #"TagPC": TagPC,
        "tag": EPC,
        #"rssi": rssi,
        'event': 'removed',
        'duration': diff
    }
    hostmqtt.publish("removed", event)

def CheckSum(uBuff, uBuffLen):
    s=bytearray(1)
    s=sum(uBuff[0:uBuffLen])
    logging.info(bytearray([s]))

    crc=((~sum(uBuff[0:uBuffLen])) & 0xFF)
    logging.info(crc)
    return crc

def rs232_checksum(the_bytes):
    return b'%02X' % (sum(the_bytes) & 0xFF)

def bit_not(n, numbits=8):
    return (1 << numbits) - 1 - n

#works..
def writeReset(ser, address, cmd, data_len=0, data=0x00):
    return writeCommand(ser, address, cmd, data_len, data)

    t = bytearray([0xA0, 0x03, address, cmd, 0xec])
    #works t = bytearray([0xA0, 0x03, 0xff, 0x70, 0xee])
    #works t = bytearray([0xA0, 0x03, 0x01, 0x70, 0xec])

    logging.info(t)

    crc = (1 << 8) - sum(bytearray([0xA0, 0x03, address, cmd])) & 0xff
    logging.info(hex( crc ))

    ser.write(t)
    return

def writeCommand(ser, address, cmd, data_len=0, data=0x00):
    length = 3+data_len    # packet length includes address, command, data and crc
    packet = bytearray(length+2)   #actual packet size has head=0xA0 and length byte
    #or just allocate a 255 length bytestring...
    
    packet[0] = 0xA0
    packet[1] = length
    packet[2] = address
    packet[3] = cmd
    if data_len > 0:
        logging.info("data: %x" % data)
        packet[4] = data
    crc = (1 << 8) - sum(bytearray([0xA0, 0x03, address, cmd])) & 0xff
    logging.info("crc: 0x%02x" % crc)
    packet[length+1] = crc
    logging.info("packet %s" %packet)
    ser.write(packet)
    logging.info("after ser.write")

cmd_reset = 0x70
cmd_set_uart_baudrate = 0x71
cmd_get_firmware_version = 0x72
cmd_set_reader_address = 0x73
cmd_set_work_antenna = 0x74
cmd_get_work_antenna = 0x75
cmd_set_output_power = 0x76
cmd_get_output_power = 0x77
cmd_set_frequency_region = 0x78
cmd_get_frequency_region = 0x79
cmd_set_beeper_mode = 0x7A
cmd_get_reader_temperature = 0x7B
cmd_read_gpio_value = 0x61
cmd_write_gpio_value = 0x62
cmd_set_ant_connection_detector = 0x63
cmd_set_temporary_output_power = 0x66
cmd_set_reader_identifier = 0x67
cmd_get_reader_identifier = 0x68
cmd_set_rf_link_profile = 0x69
cmd_get_rf_link_profile = 0x6A
cmd_get_rf_port_return_loss = 0x7E

cmd_inventory = 0x80 #Inventory EPC C1G2 tags to buffer.
cmd_read = 0x81 #Read EPC C1G2 tag(s).
cmd_write = 0x82 #Write EPC C1G2 tag(s).
cmd_lock = 0x83 #Lock EPC C1G2 tag(s).
cmd_kill = 0x84 #Kill EPC C1G2 tag(s).
cmd_set_access_epc_match = 0x85 #Set tag access filter by EPC.
cmd_get_access_epc_match = 0x86 #Query access filter by EPC.
cmd_real_time_inventory = 0x89 #Inventory tags in real time mode.
cmd_fast_switch_ant_inventory = 0x8A #Real time inventory with fast ant switch.
cmd_customized_session_target_inventory = 0x8B #Inventory with desired session and inventoried flag.
cmd_set_impinj_fast_tid = 0x8C #Set impinj FastTID function.  #(Without saving to FLASH)
cmd_set_and_save_impinj_fast_tid = 0x8D #Set impinj FastTID function.  #(Save to FLASH)
cmd_get_impinj_fast_tid = 0x8E #Get current FastTID setting.

def realTimeInventory(ser_connection, publicAddress):
    logging.info("------------------------------------- cmd_real_time_inventory")
    writeCommand(ser_connection, publicAddress, cmd_real_time_inventory, 1, 0xff)


version = ""
power = ""
region = ""
########################################
def status(ser_connection):
    global version, power, region
    # get version
    if version == "":
        logging.info("get version")
        writeCommand(ser_connection, publicAddress, cmd_get_firmware_version)
        l, t, version = readreply(ser_connection)

    # get the current antenna power
    if power == "":
        logging.info("get power")
        writeCommand(ser_connection, publicAddress, cmd_get_output_power)
        power = readreply(ser_connection)  # 4 bytes - range 0 to 0x21 in dBm

    # get the frequency region
    if region == "":
        logging.info("get region")
        writeCommand(ser_connection, publicAddress, cmd_get_frequency_region)
        region = readreply(ser_connection) # can be 3 bytes if region based, or 7 bytes if user defined.


    hostmqtt.status({
        "version": version,
        "power": power,
        "model": "desktop uhf rfid (D-10X)",
        "region": region,
        "status": "listening"})
########################################
# mosquitto_pub -t all/rfid/mode -m '{"mode": "trigger"}'
# mosquitto_pub -t all/rfid/mode -m '{"mode": "scan"}'
# mosquitto_pub -t all/rfid/mode -m '{"mode": "3000e200001606180258170069a0"}'
# mosquitto_pub -t yoga260/rfid/mode -m '{"mode": "3000e200001606180258170069a0"}'
# 


def set_mode(topic, payload):
    global MESSAGEMODE
    MESSAGEMODE = mqtt.get(payload, 'mode', 'scan')
    logging.info("setmode: %s" % MESSAGEMODE)

hostmqtt.subscribe("mode", set_mode)
hostmqtt.subscribeL("all", DEVICENAME, "mode", set_mode)

########################################
publicAddress = 0x01

#The physical interface is compatible with the RS – 232 specifications. 
# 1 start bit、8 data bits、1 stop bit、no even odd check..
#The baud rate can be set to 38400bps or 115200bps. The default baud rate is 115200bps
baudrate = 115200    # 38400 or 115200
with serial.Serial(
            '/dev/ttyUSB0', 
            timeout=0.001,
            baudrate=baudrate, 
            bytesize=serial.EIGHTBITS, 
            parity=serial.PARITY_NONE, 
            stopbits=serial.STOPBITS_ONE,
            xonxoff=0, #disable software flow control
            rtscts=0, #disable hardware (RTS/CTS) flow control
            dsrdtr=0, #disable hardware (DSR/DTR) flow control
        ) as ser_connection:
    try:
            # reset.
            logging.info("Send Reset")
            #writeCommand(ser_connection, publicAddress, cmd_reset)
            writeReset(ser_connection, publicAddress, cmd_reset)
            sleep(1)

            # get version
            logging.info("get Version")
            writeCommand(ser_connection, publicAddress, cmd_get_firmware_version)
            l, t, v = readreply(ser_connection)
            logging.info(v)

    #        logging.info("get antenna")
    #        # get the current working antenna
    #        writeCommand(ser_connection, publicAddress, cmd_get_work_antenna)
    #        a = readreply(ser_connection)
    #        logging.info(a)   # one byte

            #logging.info("set cmd_set_output_power")
            # set the current antenna power
            #writeCommand(ser_connection, publicAddress, cmd_set_output_power, 1, 0x17)
            #writeCommand(ser_connection, publicAddress, cmd_set_temporary_output_power, 1, 0x17)
            #p = readreply(ser_connection)
            #logging.info(p)   # 4 bytes - range 0 to 0x21 in dBm

            logging.info("get cmd_get_output_power")
            # get the current antenna power
            writeCommand(ser_connection, publicAddress, cmd_get_output_power)
            p = readreply(ser_connection)
            logging.info(p)   # 4 bytes - range 0 to 0x21 in dBm

            logging.info("get cmd_get_frequency_region")
            # get the frequency region
            writeCommand(ser_connection, publicAddress, cmd_get_frequency_region)
            f = readreply(ser_connection)
            logging.info(f)   # can be 3 bytes if region based, or 7 bytes if user defined.

            # logging.info("get cmd_get_reader_temperature")
            # # get reader temperature
            # writeCommand(ser_connection, publicAddress, cmd_get_reader_temperature)
            # t = readreply(ser_connection)
            # logging.info(t)   # 2 bytes first is plus/minus, second is value in c

            # logging.info(" get reader id")
            # # get reader id
            # writeCommand(ser_connection, publicAddress, cmd_get_reader_identifier)
            # id = readreply(ser_connection)
            # logging.info(id)   # 12 bytes

            # # get reader rf link profile
            # writeCommand(ser_connection, publicAddress, cmd_get_rf_link_profile)
            # rf_link_profile = readreply(ser_connection)
            # logging.info(rf_link_profile)   # 1 byte

            # set buzzer off
            # 31/08/2019 11:44:14 AM  A0 04 01 7A 00 E1
            # 31/08/2019 11:44:14 AM  A0 04 01 7A 10 D1
            # logging.info("set beeper_mode == 0x00")
            # writeCommand(ser_connection, publicAddress, cmd_set_beeper_mode, 2, 0x00)
            # buzzer_off_status = readreply(ser_connection)
            # logging.info(buzzer_off_status)   # 1 byte


            lastStatus = datetime.datetime.now()
            status(ser_connection)

            realTimeInventory(ser_connection, publicAddress)

            while True:
                try:
                    now = datetime.datetime.now()
                    diff = now-lastStatus
                    if diff.seconds > (2*60):
                        status(ser_connection)
                        lastStatus = now

                    # expire read tags if they havn't been heard from in 2 seconds
                    lastKeys = lastTimeRead.keys()
                    for EPC in lastKeys:
                        if lastTimeRead[EPC] != 0:
                            diff = now-lastTimeRead[EPC]
                            #logging.info("%s : %d microseconds" % (EPC, diff.microseconds))
                            if diff.microseconds > 200000:
                                lastTimeRead[EPC] = 0
                                sendRemoved(EPC, diff.microseconds)

                    length, packet_type, data = read_reply_real_time_inventory(ser_connection)
                    # note that there are at least 2 different replies
                    ## the response packet, and the tag info..
                    if length > 0:
                        #logging.info("read %d bytes: 0x%x" % (length, data))
                        # TODO: will get a 10 byte length response code after the timeout
                        # presumably, you then set go again...
                        if length == 10:
                            realTimeInventory(ser_connection, publicAddress)

                except Exception as ex:
                    logging.error("Exception occurred", exc_info=True)
                    logging.info("Send Reset")
                    #writeCommand(ser_connection, publicAddress, cmd_reset)
                    writeReset(ser_connection, publicAddress, cmd_reset)
                    sleep(1)
                    realTimeInventory(ser_connection, publicAddress)
    except Exception as ex:
        logging.error("Exception occurred", exc_info=True)
    except KeyboardInterrupt:
        logging.info("exit")
        logging.info("Send Reset")
        #writeCommand(ser_connection, publicAddress, cmd_reset)
        writeReset(ser_connection, publicAddress, cmd_reset)
        sleep(1)
    

hostmqtt.status({"status": "STOPPED"})
