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
from random import randint


# ************************************************
# Globals
# ************************************************

# Base addresses 
PIO_1_BASE = 0x2000
PIO_2_BASE = 0x20000000
RAM_TEST_CONTROLLER_BASE = 0x800
LPDDR2_BASE = 0x00
CUSTOM_PATTERN_GENERATOR_PATTERN_ACCESS_BASE = 0x00
CUSTOM_PATTERN_GENERATOR_CSR_BASE = 0x400
CUSTOM_PATTERN_CHECKER_PATTERN_ACCESS_BASE = 0x1000
CUSTOM_PATTERN_CHECKER_CSR_BASE = 0x1420
TWO_TO_ONE_ST_MUX_BASE = 0x440
ONE_TO_TWO_ST_DEMUX_BASE = 0x1400

# Constants 
TIMER_RESOLUTION = 16
DATA_WIDTH = 4
BUFFER_LENGTH = 1024*3
TIMEOUT = 0xFFFFFFFF
OUTPUT_RATE = 1
BLOCK_SIZE_MINIMUM = 0x400
BLOCK_SIZE_MAXIMUM = 1024*1024
BLOCK_TRAIL_DISTANCE_MINIMUM = 1
BLOCK_TRAIL_DISTANCE_MAXIMUM = 255
RAM_LENGTH_MINIMUM = 0x400
RAM_LENGTH_MAXIMUM = 1024*4#1073737728

# ************************************************
# Function Definitions
# ************************************************

# Creates random data data_packet
def create_test_data(length):
    data = []
    for x in range(0, length):
        data.append(randint(0,255))
    return data



# ************************************************
# Begining of Program
# ************************************************

# Create random data for memory
data = create_test_data(BUFFER_LENGTH)

try:
    dc590 = DC590() ## Look for the DC590
    dc590.transfer_packets('M1', 0) #
    dc590.transfer_packets('G', 0) # Set the GPIO HIGH
    
    print "\nSending data to memory"
    # Send data to memory
    print transaction_write(dc590, LPDDR2_BASE, BUFFER_LENGTH, data)
   
    print "\nReciving data from memory\n"
    
    # Read data from memory
    data_packet = transaction_read(dc590, LPDDR2_BASE, BUFFER_LENGTH)
    
    # Compare the data sent and read
    if data == data_packet:
        print "Memory Test Success !!!\n"
    else:
        print "  *** Memory test Failed ***"
    
    print "Sending data to LED's\n"
    # Send / read data from PIO thats located on the memory bus
    for y in range(0, 10):
        for x in range(0,3):   
            data = [0x01<<x]
            print "data sent: " + hex(data[0])
            # Send data to PIO
            transaction_write(dc590, PIO_2_BASE, 1, data)
            # Read data from PIO
            data_packet = transaction_read(dc590, PIO_2_BASE, 1)
            print "data read: " + hex(data_packet[0])
        for x in range(0,3):    
            data = [0x01<<(3-x)]
            print "data sent: " + hex(data[0])
            # Send data to PIO
            transaction_write(dc590, PIO_2_BASE, 1, data)
            # Read data from PIO
            data_packet = transaction_read(dc590, PIO_2_BASE, 1)
            print "data read: " + hex(data_packet[0])
    transaction_write(dc590, PIO_2_BASE, 1, [0xA])
    data_packet = transaction_read(dc590, PIO_2_BASE, 1)
    print "data read: " + hex(data_packet[0])

    dc590.transfer_packets('M1', 0) #
    dc590.transfer_packets('g', 0) # Set the GPIO LOW
    
    print "\nSending data to LED's\n"
    # Send / read data from PIO that is located on the tester bus
    for y in range(0, 10):
        for x in range(0,3):   
            data = [0x01<<x]
            print "data sent: " + hex(data[0])
            # Send data to PIO
            transaction_write(dc590, PIO_1_BASE, 1, data)
            # Read data from PIO
            data_packet = transaction_read(dc590, PIO_1_BASE, 1)
            print "data read: " + hex(data_packet[0])
        for x in range(0,3):    
            data = [0x01<<(3-x)]
            print "data sent: " + hex(data[0])
            # Send data to PIO
            transaction_write(dc590, PIO_1_BASE, 1, data)
            # Read data from PIO
            data_packet = transaction_read(dc590, PIO_1_BASE, 1)
            print "data read: " + hex(data_packet[0])
    transaction_write(dc590, PIO_1_BASE, 1, [0xA])
    data_packet = transaction_read(dc590, PIO_1_BASE, 1)
    print "data read: " + hex(data_packet[0])
    
			  
finally:
    dc590.close()
print 'Done!'

