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

# Sets the pattern payload length    
def program_custom_pattern_payload_length(dc590, pattern_length):
    Generator.set_payload_length(
        dc590,
        CUSTOM_PATTERN_GENERATOR_CSR_BASE,
        pattern_length)
    Checker.set_payload_length(
        dc590,
        CUSTOM_PATTERN_CHECKER_CSR_BASE,
        pattern_length)
    Generator.enable_start(
        dc590,
        CUSTOM_PATTERN_GENERATOR_CSR_BASE)
    Checker.enable_start(
        dc590,
        CUSTOM_PATTERN_CHECKER_CSR_BASE)

# Starts the memory test
def start_test(
        dc590,
        test_base,
        test_length,
        block_size,
        block_trail_distance):
    RamTestController.set_base_address(
        dc590,
        RAM_TEST_CONTROLLER_BASE,
        test_base)
    
    if RamTestController.set_transfer_length(
            dc590,
            RAM_TEST_CONTROLLER_BASE,
            test_length) != 0:
        print "\nYou must set the transfer length to be at least 32 bytes\n"
        return 2 # fail
    
    if RamTestController.set_block_size(
            dc590,
            RAM_TEST_CONTROLLER_BASE,
            block_size) != 0:
        print "\nYou must set the transfer block size to be at least 32 bytes\n"
        return 2 # fail
    
    if RamTestController.set_block_trail_distance(
            dc590,
            RAM_TEST_CONTROLLER_BASE,
            block_trail_distance) != 0:
        print "\nYou must set the block trail distance to be 1 to 255\n"
        return 2 # fail
    
    RamTestController.disable_concurrent_accesses(
        dc590,
        RAM_TEST_CONTROLLER_BASE)
    RamTestController.enable_start(dc590, RAM_TEST_CONTROLLER_BASE)
    return 0 # pass

# Returns 0 if pass, 1 if transfer error is detected, 2 if the test times out
def validate_results(dc590, timeout):
    counter = 0
    transfer_done = 0
    
    while True:
        transfer_done = (Checker.read_start(
            dc590, 
            CUSTOM_PATTERN_CHECKER_CSR_BASE) == 0)
        counter += 1
        if(counter >= timeout) or (transfer_done != 0):
            break
    if counter == timeout:
        print "\nThe transfer did not complete within the specified amount of time.\n"
        return 2

    if Checker.read_failure_detected(
            dc590, 
            CUSTOM_PATTERN_CHECKER_CSR_BASE) == 1:
        return 1
    # made it through the test without errors or timeout
    return 0

# ************************************************
# Begining of Program
# ************************************************

# Create random data for memory
data = create_test_data(BUFFER_LENGTH)

try:
    dc590 = DC590() ## Look for the DC590
    dc590.transfer_packets('M1', 0) # Set the GPIO HIGH
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
    
    print "\nTesting the Memory with Memory controller/tester\n"
    
    # There will be a finite payload size used and the checker cores will not 
    # stop on a failure (test software will exit when the transfer completes)    
    Generator.disable_infinite_payload_length(dc590, CUSTOM_PATTERN_GENERATOR_CSR_BASE)
    Checker.disable_infinite_payload_length(dc590, CUSTOM_PATTERN_CHECKER_CSR_BASE)
    Checker.disable_stop_on_failure(dc590, CUSTOM_PATTERN_CHECKER_CSR_BASE)
    
    RamTestController.set_timer_resolution(
        dc590,
        RAM_TEST_CONTROLLER_BASE, 
        TIMER_RESOLUTION)
    
    # Populate walking ones pattern
    # ex: [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80] 
    offset = 0
    for y in range(0,4):
        for x in range(0,8):   
                data = [0, 0, 0, 0x01<<x]
                transaction_write(
                    dc590, 
                    CUSTOM_PATTERN_GENERATOR_PATTERN_ACCESS_BASE + offset, 
                    4, 
                    data)
                transaction_write(
                    dc590, 
                    CUSTOM_PATTERN_CHECKER_PATTERN_ACCESS_BASE + offset, 
                    4, 
                    data)
                offset += 4
        for x in range(0,8):    
                data = [0, 0, 0, 0x01<<(8-x)]
                transaction_write(
                    dc590, 
                    CUSTOM_PATTERN_GENERATOR_PATTERN_ACCESS_BASE + offset,
                    4,
                    data)        
                transaction_write(
                    dc590, 
                    CUSTOM_PATTERN_CHECKER_PATTERN_ACCESS_BASE + offset, 
                    4, 
                    data)
                offset += 4
    # Set the pattern length and position for the generator and checker
    Generator.set_pattern_length(
        dc590, 
        CUSTOM_PATTERN_GENERATOR_CSR_BASE,
        DATA_WIDTH*8)
    Checker.set_pattern_length(
        dc590,
        CUSTOM_PATTERN_CHECKER_CSR_BASE,
        DATA_WIDTH*8)
    Generator.set_pattern_position(
        dc590, 
        CUSTOM_PATTERN_GENERATOR_CSR_BASE,
        0x00)
    Checker.set_pattern_position(
        dc590,
        CUSTOM_PATTERN_CHECKER_CSR_BASE,
        0x00)
        
    # Select the input and output for the custom generator and checker        
    Mux.input_select(dc590, TWO_TO_ONE_ST_MUX_BASE, 0)
    Demux.output_select(dc590, ONE_TO_TWO_ST_DEMUX_BASE, 0)
    
    failure_detected = 0 
    output_counter = 0
    bytes_tested = 0
    test_time = 0
    block_size_counter = BLOCK_SIZE_MINIMUM
    # Block size sweep loop for the major test (block keeps doubling until 
    # the max is hit)        
    while (block_size_counter <= BLOCK_SIZE_MAXIMUM) and  (failure_detected == 0):
        # block trail distance sweep loop for the major test (block trail 
        # distance keeps increasing until the max is hit)            
        block_trail_distance_counter = BLOCK_TRAIL_DISTANCE_MINIMUM
        while (block_trail_distance_counter <= BLOCK_TRAIL_DISTANCE_MAXIMUM) and (failure_detected == 0):
            # length sweep loop for the major test (length keeps doubling 
            # until the max is hit)                
            length_counter = RAM_LENGTH_MINIMUM 
            while (length_counter <= RAM_LENGTH_MAXIMUM) and (failure_detected == 0):
                
                program_custom_pattern_payload_length(dc590,length_counter)
                
                # Reset the timer built into the test controller to 0
                RamTestController.set_timer(
                    dc590, 
                    RAM_TEST_CONTROLLER_BASE,
                    0)
                start_test(
                    dc590,
                    LPDDR2_BASE,
                    length_counter,
                    block_size_counter,
                    block_trail_distance_counter)
              
                failure_detected = validate_results(dc590, TIMEOUT)
                
                #print str(failure_detected) + " failure detected variable"
                bytes_tested = length_counter
                # The timer only runs while the mains are moving data so 
                # we can read the timer result here                    
                test_time = RamTestController.read_timer(
                    dc590,
                    RAM_TEST_CONTROLLER_BASE)
                
                if failure_detected != 0:
                    print ("\n\nWalking ones test failed using a block " + 
                        "trail distance of " + str(block_trail_distance_counter) + 
                        ",\nblock size of " + str(block_size_counter) + 
                        " and transfer length of " + str(length_counter) + "\n\n")

                length_counter = length_counter * 2
            block_trail_distance_counter = block_trail_distance_counter * 2                                
        block_size_counter = block_size_counter * 2
    
    output_counter += 1
    if output_counter >= OUTPUT_RATE:
        output_counter = 0;
        # Reporting only absolute values instead of efficiency or 
        # throughput since that'll require more code space and will not fit
        # in an 8kB RAM memory efficiency = 100% * (('bytes transferred' / 
        #DATA_WIDTH) / 'clock cycles') memory throughput = 'bytes 
        # transferred' * Memory clock frequency / 'clock cycles'
        print  (str(2*bytes_tested) + " bytes transferred in " + 
            str(test_time*TIMER_RESOLUTION) + " clock cycles\n")
            # Test time is a divided clock so need to bring it back up to 
            # system ticks, data is written and read back hence the 2x reported
        
    if failure_detected != 0:
        print "\nExiting due to an error being detected or test timeout.\n"
    else:
        print "\nTest cycle complete.\n"
    
    # Returns 1 if a failure was detected, a 2 if any of the tests time 
    # out, otherwise 0 is return if all the tests pass on time
    print failure_detected
			  
finally:
    dc590.close()
print 'Done!'

