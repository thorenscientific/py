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
    
#notes = "Board 1, direct MUXOUT / ADCIN connection"
#gain = 1.0 # 1 for no sig conditioning 
    
    
    
#notes = "Board 2, Common Mode Control circuit active, 10nF caps added"
notes = "Board 1, Common Mode Control circuit active, 1MHz F0, 10nF caps added"
gain = 0.5



refmetercal = 5.00044
inmetercal = 5.00038
refmeter_comp = inmetercal / refmetercal



inmeter=AGILENT_34401A(address="GPIB0::22",debug=False)     #create the inmeter object
refmeter=AGILENT_34401A(address="GPIB0::23",debug=False)     #create the refmeter object

if inmeter.ready():
    #Use the measure command to automatically make a measurement
    inmeter.configure_dc_voltage(dvm_range=10,dvm_resolution=None,nplc=60)
    print "Take a reading from the input meter"
    voltage=inmeter.measure_dc_voltage(dvm_range=10)        #auto-ranged dc volt
    print str(voltage)      #print result
else:
    print "Input Agilent 34401 not connected"

if refmeter.ready():
    #Use the measure command to automatically make a measurement
    refmeter.configure_dc_voltage(dvm_range=10,dvm_resolution=None,nplc=60)
    print "Take a reading from the reference meter"
    voltage=refmeter.measure_dc_voltage(dvm_range=10)        #auto-ranged dc volt
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

print notes

#Set up experiment 1
numpoints = 25
negchan_start = 2.0
negchan_end = 2.0
poschan_start = 1.5
poschan_end = 4.4

negslope = (negchan_end - negchan_start) / numpoints
posslope = (poschan_end - poschan_start) / numpoints

print "experiment 1: Single ended sweep"
print "neg,pos,LTC2498,inmeter, refmeter, error (uV)"
for y in range(0,numpoints + 1): #Minus one??
    negvoltage = negslope * y + negchan_start
    posvoltage = posslope * y + poschan_start
    ltc2704(DC590ser,negchan,0,5.0, negvoltage)
    ltc2704(DC590ser,poschan,0,5.0, posvoltage)
    LTC2449voltage = avg10_LTC2449()   #1.0* ltc2449(DC590ser, 0, 1)
    involtage = inmeter.measure_dc_voltage(dvm_range=10)
    refvoltage = refmeter.measure_dc_voltage()
    error = 1000000.0 * ((float(LTC2449voltage) * (1.0/gain) * float(refvoltage) * refmeter_comp) - float(involtage))
    print str(negvoltage) + "," + str(posvoltage) + "," + str(LTC2449voltage) + "," + str(involtage) + "," + str(refvoltage)+ "," + str(error)



#Set up experiment 2
numpoints = 25
negchan_start = 1.0
negchan_end = 2.0
poschan_start = 2.0
poschan_end = 1.0

negslope = (negchan_end - negchan_start) / numpoints
posslope = (poschan_end - poschan_start) / numpoints

print "experiment 2: +/-1V sweep, VCM = 1.5V"
print "neg,pos,LTC2498,inmeter, refmeter, error (uV)"
for y in range(0,numpoints + 1): #Minus one??
    negvoltage = negslope * y + negchan_start
    posvoltage = posslope * y + poschan_start
    ltc2704(DC590ser,negchan,0,5.0, negvoltage)
    ltc2704(DC590ser,poschan,0,5.0, posvoltage)
    LTC2449voltage = avg10_LTC2449()   #1.0* ltc2449(DC590ser, 0, 1)
    involtage = inmeter.measure_dc_voltage(dvm_range=10)
    refvoltage = refmeter.measure_dc_voltage()
    error = 1000000.0 * ((float(LTC2449voltage) * (1.0/gain) * float(refvoltage) * refmeter_comp) - float(involtage))
    print str(negvoltage) + "," + str(posvoltage) + "," + str(LTC2449voltage) + "," + str(involtage) + "," + str(refvoltage)+ "," + str(error)

#Set up experiment 3
numpoints = 25
negchan_start = 2.0
negchan_end = 3.0
poschan_start = 3.0
poschan_end = 2.0

negslope = (negchan_end - negchan_start) / numpoints
posslope = (poschan_end - poschan_start) / numpoints

print "experiment 3: +/-1V sweep, VCM = 2.5V"
print "neg,pos,LTC2498,inmeter, refmeter, error (uV)"
for y in range(0,numpoints + 1): #Minus one??
    negvoltage = negslope * y + negchan_start
    posvoltage = posslope * y + poschan_start
    ltc2704(DC590ser,negchan,0,5.0, negvoltage)
    ltc2704(DC590ser,poschan,0,5.0, posvoltage)
    LTC2449voltage = avg10_LTC2449()   #1.0* ltc2449(DC590ser, 0, 1)
    involtage = inmeter.measure_dc_voltage(dvm_range=10)
    refvoltage = refmeter.measure_dc_voltage()
    error = 1000000.0 * ((float(LTC2449voltage) * (1.0/gain) * float(refvoltage) * refmeter_comp) - float(involtage))
    print str(negvoltage) + "," + str(posvoltage) + "," + str(LTC2449voltage) + "," + str(involtage) + "," + str(refvoltage)+ "," + str(error)

#Set up experiment
numpoints = 25
negchan_start = 4.0
negchan_end = 5.0
poschan_start = 5.0
poschan_end = 4.0

negslope = (negchan_end - negchan_start) / numpoints
posslope = (poschan_end - poschan_start) / numpoints

print "experiment 4: +/-1V sweep, VCM = 4.5V"
print "neg,pos,LTC2498,inmeter, refmeter, error (uV)"
for y in range(0,numpoints + 1): #Minus one??
    negvoltage = negslope * y + negchan_start
    posvoltage = posslope * y + poschan_start
    ltc2704(DC590ser,negchan,0,5.0, negvoltage)
    ltc2704(DC590ser,poschan,0,5.0, posvoltage)
    LTC2449voltage = avg10_LTC2449()   #1.0* ltc2449(DC590ser, 0, 1)
    involtage = inmeter.measure_dc_voltage(dvm_range=10)
    refvoltage = refmeter.measure_dc_voltage()
    error = 1000000.0 * ((float(LTC2449voltage) * (1.0/gain) * float(refvoltage) * refmeter_comp) - float(involtage))
    print str(negvoltage) + "," + str(posvoltage) + "," + str(LTC2449voltage) + "," + str(involtage) + "," + str(refvoltage)+ "," + str(error)

#Set DAC outputs to zero
ltc2704(DC590ser,negchan,0,5.0,0.0)
ltc2704(DC590ser,poschan,0,5.0,0.0)


DC590ser.close()
