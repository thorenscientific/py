#!/usr/bin/env python 

#    Created by: Noe Quintero
#    E-mail: nquintero@linear.com
#
#    REVISION HISTORY
#    $Revision: 2589 $
#    $Date: 2014-07-07 10:25:53 -0700 (Mon, 07 Jul 2014) $
#
#    Copyright (c) 2013, Linear Technology Corp.(LTC)
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#    The views and conclusions contained in the software and documentation are those
#    of the authors and should not be interpreted as representing official policies,
#    either expressed or implied, of Linear Technology Corp.

# Import libraries
from memory_tester_util import *
import time
import matplotlib.pyplot as plt


# ************************************************
# Globals
# ************************************************

# Base addresses 
RAM_TEST_CONTROLLER_BASE = 0x800
TWO_TO_ONE_ST_MUX_BASE = 0x440
ONE_TO_TWO_ST_DEMUX_BASE = 0x1400
LPDDR2_BASE = 0x00

# Constants 
TIMER_RESOLUTION = 65535

OUTPUT_RATE = 1
BLOCK_SIZE_MINIMUM = 0x400 
BLOCK_SIZE_MAXIMUM = 1024*1024
BLOCK_TRAIL_DISTANCE_MINIMUM = 1
BLOCK_TRAIL_DISTANCE_MAXIMUM = 255
RAM_LENGTH_MINIMUM = 0x400
RAM_LENGTH_MAXIMUM = 1024

# ************************************************
# Function Definitions
# ************************************************


# ************************************************
# Begining of Program
# ************************************************

try:

    dc590 = DC590() ## Look for the DC590
    
    dc590.transfer_packets('g', 0) # Set the GPIO low
    
    data_packet = transaction_read(dc590, RAM_TEST_CONTROLLER_BASE + 28, 4)
    print "Timer Reg:"    
    print data_packet
    
    time.sleep(5)
        
    RamTestController.disable_start(dc590, RAM_TEST_CONTROLLER_BASE)

    
    RamTestController.set_timer_resolution(
        dc590,
        RAM_TEST_CONTROLLER_BASE, 
        TIMER_RESOLUTION)
    
    # Select the input and output for the ADC        
    Mux.input_select(dc590, TWO_TO_ONE_ST_MUX_BASE, 1)
    Demux.output_select(dc590, ONE_TO_TWO_ST_DEMUX_BASE, 1)

    # Reset the timer built into the test controller to 0
    RamTestController.set_timer(
        dc590, 
        RAM_TEST_CONTROLLER_BASE,
        0)

    data_packet = transaction_read(dc590, RAM_TEST_CONTROLLER_BASE + 28, 4)
    print "Timer Reg:"    
    print data_packet

    # Set base of memory 
    RamTestController.set_base_address(
        dc590,
        RAM_TEST_CONTROLLER_BASE,
        0)
    sample_length = 536869888#*4
    # Set transfer length >= 32 bytes
    RamTestController.set_transfer_length(
            dc590,
            RAM_TEST_CONTROLLER_BASE,
            sample_length)
    
    # Set block size. >= 32 bytes. must be equal or multiple of transfer length    
    RamTestController.set_block_size(
            dc590,
            RAM_TEST_CONTROLLER_BASE,
            sample_length)
    # Set block trail distance. 1-255. the write 
    RamTestController.set_block_trail_distance(
            dc590,
            RAM_TEST_CONTROLLER_BASE,
            255)
    # Disable concurrent access
    RamTestController.disable_concurrent_accesses(
        dc590,
        RAM_TEST_CONTROLLER_BASE)
        
    # Start the test.
    RamTestController.enable_start(dc590, RAM_TEST_CONTROLLER_BASE)
    
    time.sleep(10)
    
    dc590.transfer_packets('G', 0) # Set the GPIO HIGH
    plot_sign = []
    plot_cosine = []
    sample = []
    for x in range(0,40):
        # Read data from memory
        data_packet = transaction_read(dc590, LPDDR2_BASE + 4*x, 4)
        
        sine = (int(data_packet[2])<<8) + int(data_packet[3])
        if ((sine & 0x8000) == 0x8000):	# code is < 0
            sine = (sine ^ 0xFFFF)+1    # Convert code from two's complement to binary
            sine = -sine
        plot_sign.append(sine);
  
        cosine = (int(data_packet[0])<<8) + int(data_packet[1])
        if ((cosine & 0x8000) == 0x8000):	# code is < 0
            cosine = (cosine ^ 0xFFFF)+1    # Convert code from two's complement to binary
            cosine = -cosine
        plot_cosine.append(cosine);
            
        #print "%d , %d , %d" % (x, sine, cosine)
        sample.append(int(x))

    plt.plot(sample, plot_sign, label = "sine")
    plt.plot(sample, plot_cosine, label = "cosine")

    plt.show()
    
#    print "Verifying ..."     
#    y = 0
#    for x in range(0, 1024):
#        # Read data from memory
#        data_packet = transaction_read(dc590, LPDDR2_BASE + 4*x, 4)
#        data_packet2 = transaction_read(dc590, LPDDR2_BASE + 4*(x+1), 4)
#
#        check =   data_packet2[3]- data_packet[3]
##        print check
#        if((check == 1) or (check == -255)):            
#            pass
#        else:
#            print data_packet
#            print data_packet2
#            print "Counter error at "+ str(x) 
#            print check
#            y = 1
#    if y == 0:
#        print "All Good"
    print "******************************************************"
    
    time.sleep(1)
    
    data_packet = transaction_read(dc590, sample_length - 16 , 32)
    print data_packet
    
    dc590.transfer_packets('g', 0) # Set the GPIO low
     
#    data_packet = transaction_read(dc590, RAM_TEST_CONTROLLER_BASE + 28, 4)
#    print "Timer Reg:"    
#    print data_packet
#    
#    time.sleep(1)
#    
#    data_packet_old = []
#    
#    while not (data_packet == data_packet_old):
#        data_packet_old = data_packet
#        data_packet = transaction_read(dc590, RAM_TEST_CONTROLLER_BASE + 28, 4)
#        print "Timer Reg:"    
#        print data_packet
    
    

   
    
finally:
    dc590.close()
print 'Done!'