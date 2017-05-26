################################################################################
#
# Agilent 4155 Semiconductor Parameter Analyzer Examples
#
# Author:Robert Reay
#
# Description:
#   This file contains examples of how to program the Agilent 4155.
#
# Revision History:
#   1-8-2012: Robert Reay
#     Initial code
#
################################################################################

from Agilent_4155 import *
    
def spot_measurement():
    """Make spot measurement"""
    #Spot Measurement with 1K between SMU1 and SMU2
    vi.reset()
    vi.set_timeouts(5000,5000)          #Set read timeout > measurement time
    vi.write("US")                      #Enter Flex Programming Mode
    vi.write("CN 1,2")                  #Enabled SMU1 and SMU2 
    vi.write("MM 1,1,2")                #Spot Measurement on channel SMU1,SMU2
    vi.write("CMM 1,2")                 #SMU1 reports voltage
    vi.write("DV 1,0,1,100e-3")         #SMU1 set to 1V,100e-3A max
    vi.write("DV 2,0,0,100e-3")         #SMU2 set to 0V,100e-3A max
    vi.write("XE")                      #Trigger measurement
    data=vi.query("RMD?")               #Read data with timeout
    vi.write("CL 1,2")                  #Disable SMU1 and SMU2
    vi.device_clear()
    vi.display_data(data,True)


def sampling_measurements():
    """Make sampling measurement"""
    vi.reset()
    vi.write("US")                      #Enter Flex Programming Mode
    vi.write("CN 1,2")                  #Enabled SMU1 and SMU2
    vi.write("MSC 2")                   #Abort on any error
    vi.write("MCC")                     #Clear previous sampling setup
    vi.write("MT 0.01,0.1,11")          #Hold time,interval,samples
    vi.write("MM 10,1")                 #Sampling Measurement on SMU1
    vi.write("MV 1,0,0,1,100e-3")       #SMU1 set to 0V to 1V,100e-3A max
    vi.write("DV 2,0,0,100e-3")         #SMU2 set to 0V,100e-3A max
    vi.initiate_measurement()           #Trigger measurement with polling
    data=vi.read_measurement()          #Read data with polling
    vi.write("CL")                      #Disable SMU's
    vi.device_clear()
    vi.display_data(data,True)

def staircase_sweep_measurement():
    """Make a linear sweep measurement"""
    #Staircase Sweep Measurement with 1K between SMU1 and SMU2
    vi.reset()
    vi.write("US")                      #Enter Flex Programming Mode
    vi.write("CN 1,2")                  #Enabled SMU1 and SMU2 
    vi.write("MM 2,1,2")                #Staircase sweep on channel SMU1,SMU2
    vi.write("CMM 1,2")                 #SMU1 reports voltage
    vi.write("WV 1,3,0,0,5,11,100e-3")  #SMU1,linear staircase up/down,autoscale,start,stop,step,icomp
    vi.write("WT 0,0.01,0.01")          #Pulse hold time,delay to measurement,step delay
    vi.write("DV 2,0,0,100e-3")         #SMU2 set to 0V,100e-3A max
    vi.initiate_measurement()
    data=vi.read_measurement()
    vi.write("CL")                      #Disable SMU1 and SMU2
    vi.device_clear()
    vi.display_data(data,True)
    
print "Searching for Agilent 4155"
vi=AGILENT_4155(address="GPIB0::17",debug=False)   
if vi.connected:
    print "Found "+vi.identify()+" at address %s" % (vi.address)
    print "Starting Spot Measurement"
    spot_measurement()
    print "\nStarting Sampling Measurement"
    sampling_measurements()
    print "\nStarting Staircase Sweep Measurement"
    staircase_sweep_measurement()  
else:
    print '4155 Not Found'

