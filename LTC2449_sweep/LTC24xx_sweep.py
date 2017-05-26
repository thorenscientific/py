# Test Change!
import serial
import sys
import string

from dc590_rl1009drv import *
from Agilent_34401A import *
from General_Instrument import *

def avg10_LTC2449():
    avg = 0.0
    for i in range(0,5):
        avg = avg + ltc2449(DC590ser, 0, 1)
    return avg/5.0

def avg10_HP34401(meter):
    avg = 0.0
    for i in range(0,9):
        avg = avg + float(meter.measure_dc_voltage())
    return avg/10.0


## Set up experiment
negchan_start = 0.0
negchan_end = 0.4
poschan_start = 0.4
poschan_end = 0.0
numpoints = 25

inmeter=AGILENT_34401A(address="GPIB0::22",debug=False)     #create the inmeter object
refmeter=AGILENT_34401A(address="GPIB0::23",debug=False)     #create the refmeter object

if inmeter.ready():
    #Use the measure command to automatically make a measurement
    print "Take a reading from the input meter"
    voltage=inmeter.measure_dc_voltage()        #auto-ranged dc volt
    print str(voltage)      #print result
else:
    print "Input Agilent 34401 not connected"

if refmeter.ready():
    #Use the measure command to automatically make a measurement
    print "Take a reading from the reference meter"
    voltage=refmeter.measure_dc_voltage()        #auto-ranged dc volt
    print str(voltage)      #print result
else:
    print "Reference Agilent 34401 not connected"


DC590ser = openDC590(1)


negchan = 0
poschan = 1

ltc2704(DC590ser,negchan,0,5.0, 1.0)
ltc2704(DC590ser,poschan,0,5.0, 3.0)


LTC2449voltage = 5.0* ltc2449(DC590ser, 0, 1)
involtage = inmeter.measure_dc_voltage()

print "setting both outputs to 2.5V"

print LTC2449voltage
print involtage

negslope = (negchan_end - negchan_start) / numpoints
posslope = (poschan_end - poschan_start) / numpoints

negchan_start = 0.5
negchan_end = 0.9
poschan_start = 0.9
poschan_end = 0.5
print "experiment 1: Low CM"
print "neg,pos,LTC2449,HP3456"
for y in range(0,numpoints + 1): #Minus one??
    negvoltage = negslope * y + negchan_start
    posvoltage = posslope * y + poschan_start
    ltc2704(DC590ser,negchan,0,5.0, negvoltage)
    ltc2704(DC590ser,poschan,0,5.0, posvoltage)
    LTC2449voltage = avg10_LTC2449()   #1.0* ltc2449(DC590ser, 0, 1)
    involtage = inmeter.measure_dc_voltage()
    refvoltage = refmeter.measure_dc_voltage()
    print str(negvoltage) + "," + str(posvoltage) + "," + str(LTC2449voltage) + "," + str(involtage) + "," + str(refvoltage)


negchan_start = 2.3
negchan_end = 2.7
poschan_start = 2.7
poschan_end = 2.3
print "experiment 2: Ideal CM"
print "neg,pos,LTC2449,HP3456"
for y in range(0,numpoints + 1): #Minus one??
    negvoltage = negslope * y + negchan_start
    posvoltage = posslope * y + poschan_start
    ltc2704(DC590ser,negchan,0,5.0, negvoltage)
    ltc2704(DC590ser,poschan,0,5.0, posvoltage)
    LTC2449voltage = avg10_LTC2449()   #1.0* ltc2449(DC590ser, 0, 1)
    involtage = inmeter.measure_dc_voltage()
    refvoltage = refmeter.measure_dc_voltage()
    print str(negvoltage) + "," + str(posvoltage) + "," + str(LTC2449voltage) + "," + str(involtage) + "," + str(refvoltage)


negchan_start = 4.6
negchan_end = 5.0
poschan_start = 5.0
poschan_end = 4.6
print "experiment 3: High CM"
print "neg,pos,LTC2449,HP3456"
for y in range(0,numpoints + 1): #Minus one??
    negvoltage = negslope * y + negchan_start
    posvoltage = posslope * y + poschan_start
    ltc2704(DC590ser,negchan,0,5.0, negvoltage)
    ltc2704(DC590ser,poschan,0,5.0, posvoltage)
    LTC2449voltage = avg10_LTC2449()   #1.0* ltc2449(DC590ser, 0, 1)
    involtage = inmeter.measure_dc_voltage()
    refvoltage = refmeter.measure_dc_voltage()
    print str(negvoltage) + "," + str(posvoltage) + "," + str(LTC2449voltage) + "," + str(involtage) + "," + str(refvoltage)




#Set DAC outputs to zero
ltc2704(DC590ser,negchan,0,5.0,0.0)
ltc2704(DC590ser,poschan,0,5.0,0.0)


DC590ser.close()
