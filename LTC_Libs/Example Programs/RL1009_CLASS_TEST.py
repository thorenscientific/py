################################################################################
#
# RL1009_DLL_INTERFACE test program.
#
# Author:Robert Reay
#
# Description:
# This program excercises each of the RL1009 commands. The program requires
# an Agilent 34401A DVM connected to the RL1009.
#
# Revision History:
#   11-20-2011:Robert Reay
#   Initial code
#
################################################################################

from RL1009_DLL_INTERFACE import *

dvm_address=9
#start the test
print "Starting RL1009 Class Test:\n"
print "Opening RL1009 Connection..."
r=RL1009(dvm_address)
if r.connected()==1:
    #set timeouts
    print "Command OK\n"
    read_timeout=2000
    write_timeout=2000
    print "Setting GPIB Read Timeout:%dms, Write Timeout:%dms..." % (read_timeout,write_timeout)
    r.set_timeouts(read_timeout,write_timeout)
if r.gpib_error()==0:
    #read timeouts
    print "Command OK\n"
    print "Reading GPIB Timeouts..."
    timeouts=r.get_timeouts()
if r.gpib_error()==0:
    #get RL009 version
    print "Command OK: Read Timeout:%dms, Write Timeout:%dms\n" % (timeouts[0],timeouts[1])
    print "Reading RL009 Version Info..."
    version=r.version()
if r.gpib_error()==0:
    #set GPIB address
    print "Command OK: %s\n" % version
    print "Setting GPIB address set to %d..." % dvm_address
    r.address=dvm_address
if r.gpib_error()==0:
    #read GPIB address
    print "Command OK\n"
    print "Reading back GPIB address..."
    readback_dvm_address=r.address
if r.gpib_error()==0:
    #write GPIB terminator
    print "Command OK: Address=%d\n" % readback_dvm_address   
    print "Writing GPIB terminator index..."
    r.set_terminator(3)
if r.gpib_error()==0:
    #read GPIB terminator
    print "Command OK\n"
    print "Turning RL1009 Status LED off. Hit RETURN to continue..."
    r.set_led_off()
if r.gpib_error()==0:
    s=raw_input()
    print "Setting RL1009 Status LED red. Hit RETURN to continue..."
    r.set_led_red()
if r.gpib_error()==0:
    s=raw_input()
    print "Setting RL1009 Status LED green. Hit RETURN to continue...\n"
    r.set_led_green()    
    print "Reading GPIB terminator index..."
    terminator=r.get_terminator()
if r.gpib_error()==0:
    #GPIB device clear
    print "Command OK: Terminator Index=%d\n" % terminator
    print "Executing GPIB device clear..."  
    r.device_clear(dvm_address)
if r.gpib_error()==0:
    #write *IDN? command
    print "Command OK\n"
    command="*IDN?"
    print "Writing GPIB Command: %s ..." % command
    r.write(command)
if r.gpib_error()==0:
    #read GPIB response
    print "Command OK\n"
    print "Reading GPIB Response..."
    response=r.read()
if r.gpib_error()==0:
    #GPIB Query
    print "Command OK: %s\n" % response
    command="MEASURE:VOLT:DC?"
    print "Executing GPIB Query: %s..." % command
    response=r.query(command)
if r.gpib_error()==0:
    #SRQ Poll
    reading=float(response)
    print "Command OK: DVM=%E\n" % reading
    print "Starting Serial Poll. Please Wait..."
    r.write("*CLS")
    r.write("TRIG:SOURCE IMM")
    r.write("*ESE 1")
    r.write("*SRE 32")
    r.query("*OPC?")
    r.write("CONF:VOLT:DC 10")
    r.write("VOLT:DC:NPLC 100")
    r.write("INIT") 
    r.write("*OPC")
    count=0
    start_sp=r.serial_poll()
    srq=r.srq_asserted()
    sp=r.serial_poll()
    while ((sp==start_sp) and (count<400)):
        srq=r.srq_asserted()
        sp=r.serial_poll()
        print "Serial Poll:%d SRQ:%d" % (sp,srq)
        count=count+1
    print "Poll Count: %d" % count
    command="FETCH?"
    response=r.query(command)
if r.gpib_error()==0:
    #GPIB group trigger   
    reading=float(response)
    print "Command OK: V=%E\n" % reading
    print "Testing group trigger..."
    r.write("*CLS")
    r.write("TRIG:SOURCE BUS")
    r.write("VOLT:DC:NPLC 1")
    r.write("INIT")
    r.group_trigger(str(dvm_address))
    response=r.query("FETCH?")
if r.gpib_error()==0:
    #GPIB Local
    reading=float(response)
    print "Command OK: V=%E\n" % reading
    print "Reset the DVM and switch to LOCAL mode..."
    print "System Error: %s" % r.system_error()
    r.reset()
    r.local()
if r.gpib_error()==0:
    print "Command OK\n"
else:
    print r.error_description()
r.close_connection()
print "Test Complete"
   


    
