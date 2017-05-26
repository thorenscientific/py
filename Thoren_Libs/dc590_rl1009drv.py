import serial
import sys
import string
import time
from Serial_Port_Scan import *

def openports(verbose): #to do: add verbose switch
    for n,s in scan():
        print "(%d) %s" % (n,s)
        testser = serial.Serial(n, timeout=0.1) #Open port
        testser.write("V\n") # Send version command to RL1009, safely ignored by DC590
        idstring = str(testser.read(50))
        print "Is it an RL1009?..." + idstring
        if string.find(idstring, "RL1009") >= 0:
            print "YES!!"
            RL1009 = n
        testser.write("i") # Send identify command to DC590, safely ignored by RL1009
        idstring = str(testser.read(50))
        print "Is it a DC590?..."  + idstring
        if string.find(idstring, "DC590") >= 0:
            print "YES!!"
            DC590 = n
        testser.close()
    RL1009ser = serial.Serial(RL1009, timeout=0.5)  # open first serial port
    DC590ser = serial.Serial(DC590, timeout=0.5)  # open first serial port
    return DC590ser, RL1009ser


def openDC590(verbose): #to do: add verbose switch
    for n,s in scan():
        print "(%d) %s" % (n,s)
        testser = serial.Serial(n, timeout=0.1) #Open port
        testser.write("V\n") # Send version command to RL1009, safely ignored by DC590
        idstring = str(testser.read(50))
        print "Is it an RL1009?..." + idstring
        if string.find(idstring, "RL1009") >= 0:
            print "YES!!"
            RL1009 = n
        testser.write("i") # Send identify command to DC590, safely ignored by RL1009
        idstring = str(testser.read(50))
        print "Is it a DC590?..."  + idstring
        if string.find(idstring, "DC590") >= 0:
            print "YES!!"
            DC590 = n
        testser.close()
    #RL1009ser = serial.Serial(RL1009, timeout=0.5)  # open first serial port
    DC590ser = serial.Serial(DC590, timeout=0.5)  # open first serial port
    return DC590ser




def test_all(DC590ser, RL1009ser):
    RL1009ser.write("g\n")      # Gren light on!
    RL1009ser.write("V\n")    # Get version
    print RL1009ser.read(30)
    DC590ser.write("i")      # Get ID string
    print DC590ser.read(50)
    RL1009ser.write("A30\n")	#Set address

    RL1009ser.write("R\n")
    print "read a value first: " +  RL1009ser.read(30)

    RL1009ser.write("R\n")
    readwhatever = "test string"
    readwhatever = RL1009ser.read(30)
    print "read whatever: " + readwhatever
    print "is type: "
    print readwhatever.__class__
    #readstring = readstring[1:]
    readstring =  readwhatever#.decode("utf-8")
    #print "decode to utf-8: " + readstring
    readstring = readstring[1:]
    readstring = readstring[0:(len(readstring)-2)]
    print "strip leading ACK: " + readstring
    floatvolts = float(readstring)
    print "convert to float: "
    print floatvolts




def closeports(DC590ser, RL1009ser):
    RL1009ser.close()             # close port
    DC590ser.close()
#    print "Closing ports"


# Set to 0-1 diff, OSR32768
# Using pin 14 as CS#
def ltc2449(port, channel, osr):
    port.write("gLSA8S80S00S00GgLTA8T80RRG") #Send address first,dummy conv., read real data
    readstring = "0x" + port.read(8)
    #print "read from LTC2449: " + readstring
    readint = int(readstring, 16)
    readint = readint - 2**29
    fraction = float(readint) / 2.0**29.0
    return fraction #return value as fraction of VRef



ltc2704_chA = 0
ltc2704_chA = 1
ltc2704_chA = 2
ltc2704_chA = 3
ltc2704_all_ch = 0xF


def ltc2704(port,channel, softspan, vref, vout):
    fraction = 0.5+ (0.5 * vout / vref) # re-set up for +/-5V range
    fraction = (vout / vref) # re-set up for 0-5V range
    
    daccode = int (0xFFFF * fraction)
#    print 'dac code: ' + str('{:04X}'.format(daccode))
    highbyte = daccode / 256
#    print 'highbyte: ' + str('{:02X}'.format(highbyte))
    lowbyte = daccode & 0x00FF
#    print 'lowbyte: ' + str('{:02X}'.format(lowbyte))
    tppstring = 'xS9{:1X}S{:02X}S{:02X}X'.format(channel*2, highbyte, lowbyte)
#    print tppstring
    port.write(tppstring)


def hp3456a(port, GPIB_address, init):
    if init == 1:
        port.write("A30\n")	#Set address
        port.write("WF1R4T4SM020\n") #Setup instrument
        port.read(5) #Flush buffer
    else:
        port.write("G30\n")
        port.write("R\n") 
        readstring = "test string"
        readstring = port.read(30)
        #print "got from 3456A: " + str(readstring)
        readstring = readstring[1:]
        readstring = readstring[0:(len(readstring)-1)]
        return float(readstring)


def muxboard(port, channel):
    #tppstring = "U072 K02 K13 K14 K15"
    tppstring = 'U{:02X}2 K02'.format(channel)
#    print "tppstring: " + tppstring
    port.write(tppstring)
    #time.sleep(1)
    #port.write("UFF2 U351 K01")
    
        
#def muxboard_test()
#print "testing mux board"
#for y in range(0,10):
#    for x in range(0, 15):
#        tppstring = 'U{:02X}2 K02'.format(x)
#        print "tppstring: " + tppstring
#        DC590ser.write(tppstring)
#        #muxboard(DC590ser, x)
#        time.sleep(0.25)


