# test_ltccap.py - An example program to test the Python LtcCap
#
# Copyright (c) 2011 Linear Technology Corporation
# This software is property of Linear Technology Corporation (LTC) and is being provided for 
# example purposes only. Sale or redistribution of this software or any of its parts requires 
# prior written permission from LTC.
# This software is provided AS IS, and WITHOUT WARRANTY OF ANY KIND, by using this software you
# agree that LTC is not responsible for any damages of any kind directly or indirectly related
# to the possesion or use of this software.
# 
# Created by Jeremy Sorensen; jsorensen@linear.com
# Dec 02, 2011
# $ LastChangedBy: $
# $ Date: $
# $ Revision: $

# import the ltccap module
from ltccap import *

# number of samples to read
NSAMPS = 32

try:
    # Create the LtcCap object representing the ADC, passing in the parameters
    # NOTE: This is probably wrong for your setup, change these parameters to match your setup
    # adc = LtcCap.create(DC718, 1, 16, 16, True, POS_EDGE, CMOS)

    # Create the LtcCap object representing the ADC, allowing the user to enter the device
    # parameters interactively through a dialog box
    adc = LtcCap.createFromDialog()
    
    # read NSAMPS points
    if adc.nChannels == 2:
        # two channel read
        data1, data2 = adc.read(NSAMPS, IMMEDIATE)
        # now print the data
        print("Data: ")
        for i in range(len(data1)):
            print("" + str(data1[i]) + "," + str(data2[i]))
    else:
        # single channel read
        data = adc.read(NSAMPS, IMMEDIATE)
        # now print the data
        print("Data: ")
        for d in data:
            print(d)

except LtcCapError as e:
    print("Error: " + e.value)
    

