################################################################################
#
# DC590 Examples
#
# Author:Robert Reay
#
# Description:
#   This program demonstrates how to use the DC590 class
#
# Revision History:
#   1-6-2013: Robert Reay
#   Initial code
#
################################################################################

from DC590_CLASS import *
from Macros import get_integer

print "Searching For DC590..."
dc590=DC590_CLASS()                               
print "DC590 count= %d" % dc590.count
for i in range(dc590.count):
      print "dc590[%d] on COM%d" % (i,dc590.port_list[i]+1)
if dc590.count>0:    
    #**** test variables ****
    i2c_address=0x10                  #i2c_address
    command=0x3F                      #test command byte
    data_byte=0xF0                    #test data byte
    data_word=0xFF00                  #test data word
    result=0                          #test input data
    data_buffer=[0x80,0x00]           #test data buffer

    #**** i2c routine tests ****
    dc590.i2c_mode()
    data=dc590.i2c_write_buffer(i2c_address,data_buffer)             #s,address+w,data_buffer,p 
    
    #**** smbus routine tests ****
    dc590.i2c_mode()
    dc590.smbus_write_byte(i2c_address,command,data_byte)            #s,address+w,command,data byte,p
    dc590.smbus_write_word(i2c_address,command,data_word)            #s,address+w,command,data word msb first,p
    dc590.smbus_write_word(i2c_address,command,data_word,lsb_first)  #s,address+w,command,data word lsb first,p                                          
    dc590.smbus_write_buffer(i2c_address,command,data_buffer)        #s,address+w,command,data_buffer,p  
    result=dc590.smbus_read_string_buffer(i2c_address,command,2)     #s,address+w,command,s,address+r,2 data bytes,p
    result=dc590.smbus_read_byte_buffer(i2c_address,command,2)       #s,address+w,command,s,address+r,2 data bytes,p
    if dc590.ack:
      print result
    else:
      print "Slave did not acknowledge"
      
##    #**** LTC2400 Delta Sigma Converter tests ****
##    dc590.spi_mode()
##    for i in range(2):
##      data=dc590.read_LTC24XX_32bit(0x80)
##      print "Normalized Reading: %1.7f" % data

    #**** SPI tests *****
    dc590.spi_mode()
    dc590.spi_write_byte(command,data_byte)           #CS low,command,data_byte,CS high   
    dc590.spi_write_word(command,data_word)           #CS low,command,data word msb first,CS high
    dc590.spi_write_word(command,data_word,lsb_first) #CS low,command,data word lsb first,CS high
    data_buffer=[0x3F,0x80,0x00]
    dc590.spi_write_buffer(data_buffer)               #CS low,data_buffer,CS high
    output_buffer=[0x80]                          
    data=dc590.spi_read_string_buffer(output_buffer,4)#CS low, write MOSI 1 byte, read MISO 4 bytes,CS high
    data=dc590.spi_read_byte_buffer(output_buffer,4)  #CS low, write MOSI 1 byte, read MISO 4 bytes,CS high
    print data

    #**** Multiple dc590's ****
    if dc590.count>1:
      dc590.device_index=0
      dc590.spi_write_word(0x3F,0xF000)
      dc590.device_index=1
      dc590.spi_write_word(0x3F,0xFFFF)

    #**** IO Pins ****
    for i in range(2):
      dc590.c2=0 #turn on LED on pin C2
      sleep(0.5)
      dc590.c2=1 #turn off LED on pin C2
      sleep(0.5)
          
        
          
          
