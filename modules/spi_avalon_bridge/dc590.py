#!/usr/bin/env python

#    Created by: Noe Quintero
#    E-mail: nquintero@linear.com
#
#    REVISION HISTORY
#    $Revision: 2581 $
#    $Date: 2014-06-26 15:51:36 -0700 (Thu, 26 Jun 2014) $
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
#
#    The Linear Technology Linduino is not affiliated with the official Arduino team.
#    However, the Linduino is only possible because of the Arduino team's commitment
#    to the open-source community.  Please, visit http://www.arduino.cc and
#    http://store.arduino.cc , and consider a purchase that will help fund their
#    ongoing work.

import serial
import time
from Serial_Port_Scan import *

# Note: the Linduino needs to be in SPI Mode 1 when running the DC590 sketch

# Open a serial connection with Linduino
class DC590:
     
    def __init__(self):
        self.open()

    def open(self):
        # Look for the DC590
        print "Looking for DC590 ..."
        ports = scan()
        number_of_ports = len(ports)
        print "\nLooking for COM ports ..." 
        print ports
        for x in range(0,number_of_ports):
            testser = serial.Serial(ports[x][1], 115200, timeout = 0.1) # Opens the port
            time.sleep(2)   # A delay is needed for the Linduino to reset
            try:
                id_linduino = testser.read(50) # Remove the hello from buffer
                
                # Get ID string
                testser.write("i") 
                id_linduino = testser.read(50)
                
                if id_linduino[20:25] == "DC590":
                    DC590 = ports[x][1]
            except:
                pass
            testser.close()
        
        try:
            self.port = serial.Serial(DC590, 115200, timeout = 0.05)  # Open serial port
            time.sleep(2)           # A delay is needed for the Linduino to reset
            self.port.read(50)     # Remove the hello from buffer
            print "\nFound DC590!"
        except:
            print "DC590 was not detected"
        
    def close(self):
        try:
            self.port.close()  # Close serial port
            return 1
        except:
            return 0
            
    def transfer_packets(self, packets, return_size):
        try:
            self.port.write(packets)                       # Send packet
            packet = self.port.read((return_size*2 + 4)*2) # Receive packet
            return packet
        except:
            return 0

#*************************************************
# Function Tests
#*************************************************

if __name__ == "__main__":
    
    
    try:
        dc590 = DC590() # Look for the DC590
        
        print dc590.transfer_packets('xRRRRX',4)
        
    finally:
        dc590.close()
    print "Test Complete"