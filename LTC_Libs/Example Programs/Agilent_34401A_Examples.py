################################################################################
#
# Agilent 34401A 6.5 digit DVM coding example
#
# Author:Robert Reay
#
# Description:
#   This file contains examples of how to take measurements with the Agilent 34401A DVM
#
# Revision History:
#   1-5-2013: Robert Reay
#     Remove the Find Address routine
#   9-25-2012: Robert Reay
#     Initial code
#
################################################################################

from Agilent_34401A import *                #import the dvm routines
print "Searching for Agilent 34401A"
dvm=AGILENT_34401A(debug=False)             #create the dvm object
if dvm.connected:
    print "Found "+dvm.identify()+" at address %s" % (dvm.address)
    dvm.reset()
    #Use the measure command to automatically make a measurement
    print "Auto Range Voltage Measurement"
    voltage=dvm.measure_dc_voltage()        #auto-ranged dc volt
    print "V=%2.6f\n" % float(voltage)      #print result

    print "Voltage Measurement,Range=1V,Resolution=1uV"        
    voltage=dvm.measure_dc_voltage(1,1e-6)  #dc volts on 1V range,1uV resolution
    print "V=%2.6f\n" % float(voltage)      #print result

    #Long Measurement Example
    #Use the configure command to get more control of the measurement.
    #The initiate_measurement routine inserts the *OPC? (operation complete)
    #command into the dvm queue, which forces the dvm to wait for the
    #measurement to be completed before responding to a GPIB read. The GPIB read
    #timeout needs to be extended to a value longer than the expected measurement time.
    print "Voltage Measurement with 100 Line Cycle Integration"
    dvm.trigger_immediate()                 #measurement starts when initiated
    dvm.configure_dc_voltage(1,1e-6,100)    #configure dc volts with 100 line cycle integration (~5s)    
    dvm.set_timeouts(6000,100)              #extend the GPIB read timeout to 6s
    dvm.initiate_measurement()              #initiate measurement
    voltage=dvm.read_measurement()          #read the result from memory
    print "V=%2.6f\n" % float(voltage)      #print result

    #Serial Polling Example
    #Poll the status register of the dvm to determine when the measurement has completed.
    #This allows the program to do something else while waiting for the measurement
    #to complete.
    print "Starting Serial Polling Measurement"
    dvm.trigger_immediate()                 #measurement starts when initiated
    dvm.configure_dc_voltage(1,1e-6,100)    #configure dc volts with 100 line cycle integration (~5s) 
    dvm.initiate_measurement(True)          #initiate the measurement with serial polling enabled
    for t in range(10):                     #start a polling loop with 10s timeout for safety
        print t
        if dvm.measurement_complete():      #check the status register for operation complete
            break
        dvm.wait(1)                         #if not complete, wait 1s
    voltage=dvm.read_measurement()          #read the result from memory        
    print "V=%2.6f\n" % float(voltage)      #print result

    #User (bus) Triggered Example
    #Set the dvm to wait for a software trigger to start the measurement
    print "Starting User Triggered Measurement"
    dvm.configure_dc_voltage(1,1e-6,100)    #configure dc volts with 100 line cycle integration (~5s)
    dvm.set_timeouts(6000,100)              #extend the GPIB read timeout to 6s
    dvm.trigger_bus()                       #set the trigger to bus
    dvm.initiate_measurement()              #initiate the measurement. Doesn't start until bus trigger
    dvm.display_text("Waiting")             #display message on meter
    raw_input("Press RETURN to start measurement")
    dvm.display_text("Measuring")
    dvm.trigger()                           #trigger the measurement
    voltage=dvm.read_measurement()          #read the result from memory after the operation is complete       
    print "V=%2.6f\n" % float(voltage)      #print result

    #Multiple Trigger Measurement
    print "Multiple Triggered Measurement"
    dvm.configure_dc_voltage(1,1e-6,10)     #configure dc volts with 10 line cycle integration
    dvm.trigger_immediate()                 #set the trigger to immediate
    dvm.trigger_count(5)                    #take 5 measurements
    dvm.display_text("Waiting")
    raw_input("Press RETURN to start measurement")
    dvm.initiate_measurement()              #initialize the measurement
    dvm.display_text("Measuring")
    readings=dvm.read_measurement()         #read the results
    voltages=readings.split(",")            #split the readings into the voltage array
    for i in range(len(voltages)):
        print "V"+str(i)+"=%2.6f" % float(voltages[i])  #print results
    dvm.display_text("Done")
    print "\nProgram Complete\n"
else:
    print "Agilent 34401 not found"
