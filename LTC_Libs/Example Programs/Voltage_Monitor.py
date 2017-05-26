################################################################################
#
# Voltage Monitor
#
# Author:Robert Reay
#
# Description:
#   Use the Agilent 34401A DVM to monitor a voltage at a regular inverval. The
# data will be written to the screen, and to a tab delimited file. The data can
# be cut and pasted from the output window to EXCEL.
#   The main loop is wraped in a try loop in order to capture a CNTRL-C input from
# the user to abort the measurement early while still maintaining the previously taken data.
#
# Revision History:
#   9-17-2012: Robert Reay
#     Add the search for the dvm at the beginning of the program
#   9-10-2012: Robert Reay
#     Initial code
#
################################################################################

from Agilent_34401A import *    #import the dvm routines

#global variables
time_interval=5                 #The measurement interval in seconds
max_time=360000                 #The maximum time
time=-1*time_interval           #Initialize the current time in seconds
file_name="Monitor.tsv"         #The data file name
voltage=0                       #The voltage measurement

#start program
print "Searching for Agilent 34401"
dvm=AGILENT_34401A()            #The dvm object
if dvm.connected:       
    data_file=open(file_name,"w") #Open the file for writing
    #Print The Header
    print "Starting Measurement. Type CONTROL-C to abort.\n\n"
    outstring="Time(s)\tVoltage(V)"
    print outstring
    data_file.write(outstring+"\n")
    #Start the Measurement
    try:                                            
        while time<max_time :
            time=time+time_interval                 #Increment the time interval
            voltage=float(dvm.measure_dc_voltage()) #Measure the dvm voltage
            outstring="%d\t%3.6f" % (time,voltage)  #Format the data and print
            print outstring                         #Print the data to the screen
            data_file.write(outstring+"\n")         #Print the data to the file
            for i in range(time_interval):          #Wait for next time point
                dvm.wait(1)
        print "\nProgram Complete.\n\n"
        data_file.close()                           #close the data file    
    except KeyboardInterrupt:                       #handle CNTRL-C exception
        data_file.close()                           #close the data file
        print "\nKeyboard interrupt detected. Closing the file and exiting the program.\n\n"
else:
  print "Agilent 34401A not Found"

    
