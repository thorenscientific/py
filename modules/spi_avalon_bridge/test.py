#    Created by: Noe Quintero
#    E-mail: nquintero@linear.com
#
#    REVISION HISTORY
#    $Revision: 2581 $
#    $Date: 2014-06-26 15:51:36 -0700 (Thu, 26 Jun 2014) $

#    Copyright (c) 2013, Linear Technology Corp.(LTC)
#    All rights reserved.

#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:

#    1. Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.

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

#    The views and conclusions contained in the software and documentation are those
#    of the authors and should not be interpreted as representing official policies,
#    either expressed or implied, of Linear Technology Corp.

# import libraries
from ltc_spi_avalon import *
from random import randint

# Constants 
CONST_BUFFER_LENGTH = 1024
CONST_MEMORY_BASE = 0x0000
CONST_PIO_BASE = 0x2000

# Creates random data 
def create_test_data(length):
    data = []
    for x in range(0, length):
        data.append(randint(0,255))
    return data


# Beginning of Program
# Create random data for memory
data = create_test_data(CONST_BUFFER_LENGTH)

try:    
    dc590 = DC590() # Look for the DC590
    
    print "\nSending data to memory"
    # Send data to memory
    packet = transaction_write(dc590, CONST_MEMORY_BASE, CONST_BUFFER_LENGTH, data)
    print packet
    print "\nReciving data from memory\n"
    
    # Read data from memory
    data_packet = transaction_read(dc590, CONST_MEMORY_BASE, CONST_BUFFER_LENGTH)
    
    # Compare the data sent and read
    if data == data_packet:
        print "Memory Test Success !!!\n"
    else:
        print "  *** Memory test Failed ***"
    
    print "Sending data to LED's\n"
    # Send / read data from PIO 
    for y in range(0, 10):
        for x in range(0,7):   
            data = [0x03<<x]
            print "data sent: " + hex(data[0])
            # Send data to PIO
            packet = transaction_write(dc590, CONST_PIO_BASE, 1, data)
            # Read data from PIO
            data_packet = transaction_read(dc590, CONST_PIO_BASE, 1)
            print "data read: " + hex(data_packet[0])
        for x in range(0,7):    
            data = [0x03<<(6-x)]
            print "data sent: " + hex(data[0])
            # Send data to PIO
            packet = transaction_write(dc590, CONST_PIO_BASE, 1, data)
            # Read data from PIO
            data_packet = transaction_read(dc590, CONST_PIO_BASE, 1)
            print "data read: " + hex(data_packet[0])
    transaction_write(dc590, CONST_PIO_BASE, 1, [0xAA])
    data_packet = transaction_read(dc590, CONST_PIO_BASE, 1)
    print "data read: " + hex(data_packet[0])
finally:
    dc590.close()
print "Test Complete"