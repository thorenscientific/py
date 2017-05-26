################################################################################
#
# LTC2657 Example
#
# Author:Robert Reay
#
# Description:
#   This program demonstrates how to communicate with an LTC2657 16-bit Octal
# I2C DAC using a DC590B and demo board 1529A.
#
# Revision History:
#   9-11-2012: Robert Reay
#   Initial code
#
################################################################################

from DC590_CLASS import *
from Macros import get_integer


#LTC2657 Command Codes
#OR'd together with the DAC address to form the command byte
cmd_write=              0x00  # Write to input register n
cmd_update=             0x10  # Update (power up) DAC register n
cmd_write_update=       0x30  # Write to input register n, update (power-up) all
cmd_power_down=         0x40  # Power down n
cmd_power_down_all=     0x50  # Power down chip (all DAC's and reference)
cmd_internal_reference= 0x60  # Select internal reference (power-up reference)
cmd_external_reference= 0x70  # Select external reference (power-down internal reference)
cmd_no_operation=       0xF0  # No operation

#LTC2657 DAC addresses
DAC_A=     0x00
DAC_B=     0x01
DAC_C=     0x02
DAC_D=     0x03
DAC_E=     0x04
DAC_F=     0x05
DAC_G=     0x06
DAC_H=     0x07
DAC_ALL=   0x0F

#global variables
command=cmd_write_update    #DAC command. Upper 4 bits of command byte
address=DAC_ALL             #DAC address. Lower 4 bits of command byte
code=0x8000                 #16-bit DAC code
i2c_address=0x20            #i2c_address
    
def print_prompt():
    print "\n***********************************************\n"
    print "DAC variables:"
    print "  code=0x%X" % (code)
    print "  command=0x%X" % (command)
    print "  address=0x%X" % (address)
    print "  i2c_address=0x%X\n" % (i2c_address)
    
    print "Command Summary:"
    print "  1-Write To DAC "
    print "  2-Set the DAC code" 
    print "  3-Set the DAC command"
    print "  4-Set the DAC address"
    print "  5-Set the i2c address"
    print "  6-Exit\n"
    
#Start Main Program

dc590=DC590_CLASS()  # Create DC590 Object
if dc590.count>0:    # Check for a connected DC590
    dc590.i2c_mode() # Setup i2c communications   
    while 1:
        print_prompt()
        data=get_integer("Enter Command: ",1,6)   
        if data==1:
            #ack=dc590.smbus_write_word(i2c_address,command | address,code)             #update DAC via dc590           
            #here is alternative way to send data
            data_buffer=[0x80,0x01]                                                   #set i2c data
            ack=dc590.smbus_write_buffer(i2c_address,command | address,data_buffer)   #write the data
            if ack:
                print "DAC updated"    
            else:
                print "DAC did not acknowledge"
        elif data==2:
            #DAC Code
            code=get_integer("Enter the DAC code: ",0,0xFFFF)
        elif data==3:
            #DAC command
            command=get_integer("Enter the DAC command: ",0,0xF0)        
        elif data==4:
            #DAC address
            address=get_integer("Enter the DAC address: ",0,0x0F)
        elif data==5:
            #i2c address
            i2c_address=get_integer("Enter the i2c address: ",0,0xFF)
        elif data==6:
            #Exit
            print "\nExiting Program"
            break        
else:
    print "DC590 Not Connected"
        
      
        
        
