#!/usr/bin/python3

#OMG https://lo.calho.st/projects/the-fruits-of-some-recent-arduino-mischief/

import serial
from time import sleep

# for UHF RFID reader - the yellow one...

def readreply(ser):
    packet_type = ser.read(1)
    print(packet_type)
    # assert(packet_type == 0xA0)
    p = int.from_bytes(packet_type, byteorder="big")
    print(p)
    if p != 0:
        print("type == %s" % format(p, '#04x'))

        l = ser.read(1)
        length = int.from_bytes(l, byteorder="big")
        print("length == %u (0x%x)" % (length, length))

        if length > 0:
            a = ser.read(1)
            d = ser.read(length-2)
            c = ser.read(1)
            address = int.from_bytes(a, byteorder="big")
            data = int.from_bytes(d, byteorder="big")
            crc = int.from_bytes(c, byteorder="big")
            print("READ: address = %s data == %s" % (format(address, '#04x'), format(data, '#04x')))

            return data
    return "nothing"

def CheckSum(uBuff, uBuffLen):
    s=bytearray(1)
    s=sum(uBuff[0:uBuffLen])
    print(bytearray([s]))

    #uSum=bytearray(1)
    #for i in range(0, uBuffLen):
    #    uSum[0] = uSum[0] + uBuff[i]
    #uSum[0] = ~(uSum[0]) + 0x01
    #print(uSum[0])
    #return uSum[0]

    crc=((~sum(uBuff[0:uBuffLen])) & 0xFF)
    print(crc)
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

    print(t)

    crc = (1 << 8) - sum(bytearray([0xA0, 0x03, address, cmd])) & 0xff
    print(hex( crc ))

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
        print("data: %x" % data)
        packet[4] = data
    crc = (1 << 8) - sum(bytearray([0xA0, 0x03, address, cmd])) & 0xff
    print("crc: 0x%02x" % crc)
    packet[length+1] = crc
#    packet[4] = crc
    print(packet)
    ser.write(packet)

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


publicAddress = 0x01

#The physical interface is compatible with the RS – 232 specifications. 
# 1 start bit、8 data bits、1 stop bit、no even odd check..
#The baud rate can be set to 38400bps or 115200bps. The default baud rate is 115200bps
baudrate = 115200    # 38400 or 115200
with serial.Serial(
        '/dev/ttyUSB0', 
        timeout=None, 
        baudrate=baudrate, 
        bytesize=serial.EIGHTBITS, 
        parity=serial.PARITY_NONE, 
        stopbits=serial.STOPBITS_ONE,
        xonxoff=0, #disable software flow control
        rtscts=0, #disable hardware (RTS/CTS) flow control
        dsrdtr=0, #disable hardware (DSR/DTR) flow control
    ) as ser_connection:
    #try:
        # reset.
        print("Send Reset")
        #writeCommand(ser_connection, publicAddress, cmd_reset)
        writeReset(ser_connection, publicAddress, cmd_reset)
        sleep(1)

        # get version
        print("get Version")
        writeCommand(ser_connection, publicAddress, cmd_get_firmware_version)
        v = readreply(ser_connection)
        print(v)

#        print("get antenna")
#        # get the current working antenna
#        writeCommand(ser_connection, publicAddress, cmd_get_work_antenna)
#        a = readreply(ser_connection)
#        print(a)   # one byte

#        print("get cmd_get_output_power")
#        # get the current antenna power
#        writeCommand(ser_connection, publicAddress, cmd_get_output_power)
#        p = readreply(ser_connection)
#        print(p)   # 4 bytes - range 0 to 0x21 in dBm

#        print("get cmd_get_frequency_region")
#        # get the frequency region
#        writeCommand(ser_connection, publicAddress, cmd_get_frequency_region)
#        f = readreply(ser_connection)
#        print(f)   # can be 3 bytes if region based, or 7 bytes if user defined.

#        # get reader temperature
#        writeCommand(ser_connection, publicAddress, cmd_get_reader_temperature)
#        t = readreply(ser_connection)
#        print(t)   # 2 bytes first is plus/minus, second is value in c

#        print(" get reader id")
#        # get reader id
#        writeCommand(ser_connection, publicAddress, cmd_get_reader_identifier)
#        id = readreply(ser_connection)
#        print(id)   # 12 bytes

#        # get reader rf link profile
#        writeCommand(ser_connection, publicAddress, cmd_get_rf_link_profile)
#        rf_link_profile = readreply(ser_connection)
#        print(rf_link_profile)   # 1 byte

        print("cmd_real_time_inventory")
        writeCommand(ser_connection, publicAddress, cmd_real_time_inventory, 1, 0xff)
        while True:
            tag_data = readreply(ser_connection)
            # note that there are at least 2 different replies
            ## the response packet, and the tag info..
            print("read : 0x%x" % tag_data)

            # TODO: will get a 10 byte length response code after the timeout
            # presumably, you then set go again...

