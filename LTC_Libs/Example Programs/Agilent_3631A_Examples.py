################################################################################
#
# Agilent E3631A Triple Power Supply coding example
#
# Author:Robert Reay
#
# Description:
#   This file contains examples of how to program the E3631A power supply
#
# Revision History:
#   1-5-2013: Robert Reay
#     Remove the find_instrument call
#   9-25-2012: Robert Reay
#     Initial code
#
################################################################################

from Agilent_E3631A import *                    #import the power supply routines

print "Searching for Agilent 3631A"
ps=AGILENT_E3631A(debug=True)
if ps.connected:
    ps.reset()                               
    print "Found "+ps.identify()+" at address %s" % (ps.address)
    #Simple Supply Update and Measure
    print "Simple Supply Update and Measure"
    ps.apply(1,4,1)                           #set P5V supply to 4V, 1A
    ps.apply(2,20,0.5)                        #set P25V supply to 25V, 500mA
    ps.apply(3,-25,1)                         #set N25V supply to -25V, 1A
    ps.output_on()
    for i in range(3):
        current=float(ps.measure_current(i))    #measure the current
        voltage=float(ps.measure_voltage(i))    #measure the voltage
        print "I%d=%2.3fA V%d=%2.3fV" %(i+1,current,i+1,voltage) #print result
    #Software trigger
    #This example arms all of the supplies, then updates them simultaneously
    #using the trigger command
    print '\nSoftware Trigger Simultaneous Update Example'
    ps.reset()          
    ps.couple_all()
    ps.trigger_bus()
    ps.configure(1,5,1)
    ps.configure(2,12,1)
    ps.configure(3,-12,1)
    ps.output_on()
    ps.init()
    s=raw_input('Press the ENTER key to update supplies')
    ps.trigger()
    print "\nProgram Complete\n"
else:
    print 'Power Supply Not Found'
