################################################################################
#
# Zener Drift
#
# Author:Robert Reay
#
# Description:
#   Use the Agilent 34970 DVM and an Agilent E3631A to monitor the GATE pin
# voltage on 20 LT4363's on a test board. The data will be written to the screen, that
# can then be cut and pasted into EXCEL. The minus input on each channel is conected
# to ground. The P25 supply is used on the E3631A.
#
# Revision History:
#   1-5-2013: Robert Reay
#     Revise code for new drivers
#   11-13-2012: Robert Reay
#     Initial code
#
################################################################################

from Agilent_34970A import *    #import the dvm routines
from Agilent_E3631A import *    #import the supply routines

#global variables
dvm_address="GPIB0::9"          #The dvm gpib address
supply_address="GPIB0::5"       #The supply gpib address
ready=False      
supply_voltage=12               #The supply voltage
current_limit=0.1               #The dupply current limit
channel_list=[]

#start program
print "\nSearching for Instruments\n"
dvm=AGILENT_34970A(address=dvm_address)   #The dvm object
ps=AGILENT_E3631A(address=supply_address) #The supply object
if dvm.connected:
    if ps.connected:
        ready=True;
    else:
        print "Agilent E3631A not found"
else:
    print "Agilent 34970A not Found"
if ready:
    print "%s at address %s" % (dvm.identify(),dvm.address)
    print "%s at address %s" % (ps.identify(),ps.address)
    print "Turning On Supply and waiting 2s\n"
    for i in range(101,121):channel_list.append(i)          #build the channel list [101,102, ... 120]
    ps.apply(2,supply_voltage,current_limit)                #set the supply voltage
    ps.output_on()                                          #turn on supply
    ps.wait(2)                                              #wait for 2 second to settle
    reading=ps.measure_voltage(2)                           #measure the supply voltage
    print "Supply Voltage \t%2.3f" % float(reading)         #print the supply current
    reading=ps.measure_current(2)                           #measure the supply current
    print "Supply Current \t%2.6f" % float(reading)         #print the supply current
    print "Starting Measurement ...\n"
    dvm.trigger_immediate()                                 #measurement starts when initiated
    dvm.configure_dc_voltage(channel_list,nplc=20)          #configure dc volts,20 line cycle integration     
    dvm.impedance_high()                                    #set high impedance
    dvm.set_timeouts(6000,100)                              #extend the GPIB read timeout to 6s
    dvm.initiate_measurement()                              #initiate measurement
    readings=dvm.read_measurement()                         #read the result from memory
    voltages=readings.split(",")                            #split the readings into the voltage array
    for i in range(len(voltages)):
      print "V"+str(i+1)+"\t%2.3f" % float(voltages[i])     #print results   
else:
    print "Aborting measurement"
print "\nProgram Complete\n"
    
