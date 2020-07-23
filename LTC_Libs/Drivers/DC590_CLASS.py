################################################################################
#
# DC590 Class
#
# Author:Robert Reay
#
# Description:
#   This file contains a class driver for the LTC DC590 USB to serial converter
# using a COM port instead of the ftdi usb driver. The class maintains a list
# of COM ports that have a DC590 connected so that multiple DC590's can be used
# simultaneously. The COM ports are scanned for DC590's the the class constructor
# is called.
#  The class includes standard i2c, smbus and spi communications routines as well
# as routines to set the I/O bits on the DC590B that can be used to control relays
# or LED's.
#
# Revision History:
#   9-14-2012:Robert Reay
#     Update IO/routines
#   7-9-2012:Robert Reay
#     Initial code
#     
################################################################################

import serial
from time import sleep

#constants
msb_first=0  #send data msb first
lsb_first=1  #send data lsb first

class DC590_CLASS(object):
    """DC590 USB to Serial Driver Class."""

    #DC590 constructor and private methods
    
    def __init__(self,timeout=0.1,show_errors=False,baudrate=115200,Linduino=False):
        """DC590 Class Constructor."""
        self.__timeout=timeout                #Communication timeout
        self.__ack=True                       #I2C subordinate ack status
        self.__count=0                        #The number of DC590's connected
        self.__connected=False                #Serial connection OK
        self.__port_list=[]                   #List of COMM ports with DC590's connected
        self.__error_list=[]                  #List of errors
        self.__device_index=0                 #Current DC590 index
        self.__port=0                         #The current COM port
        self.__show_errors=show_errors        #Show errors as they occur
        self.__b0=0                           #DC590 I/O bit B0
        self.__b1=0                           #DC590 I/O bit B1
        self.__b2=0                           #DC590 I/O bit B2
        self.__c0=0                           #DC590 I/O bit C0
        self.__c1=0                           #DC590 I/O bit C1
        self.__c2=0                           #DC590 I/O bit C2
        self.__baudrate=baudrate              #set the default baudrate
        self.__Linduino=Linduino              #set to TRUE if Linduino emulating DC590
        self.scan()                           #Scan the COM ports for DC590's and build the port list

    def __del__(self):
        """DC590 Class Destructor."""
        self.close_connection()
        self.__connected=False
      
    #Private Property Interface Routines

    def __get_ack(self):
        """Get the i2c ack status."""
        return self.__ack
    
    def __get_count(self):
        """Get the DC590 device count"""
        return self.__count

    def __get_port(self):
        """Get the DC590 port"""
        return self.__port_list[self.__device_index]

    def __get_device_index(self):
        """Get the DC590 device index"""
        return self.__device_index
    
    def __set_device_index(self,new_index):
        """Set the device index"""
        if new_index<self.__count:
            self.__device_index=new_index
            if self.__connected:
                self.close_connection()
                self.__open_new_connection() 

    def __get_port_list(self):
        """Get the DC590 port list"""
        return self.__port_list
    
    def __getb0(self):
        """Get the b0 bit status."""
        return self.__cb

    def __setb0(self,value):
        """Set the b0 bit."""
        self.__b0=value
        if value==0:
            self.write("K00")
        else:
            self.write("K10")

    def __getb1(self):
        """Get the cb bit status."""
        return self.__b1

    def __setb1(self,value):
        """Set the b1 bit."""
        self.__b1=value
        if value==0:
            self.write("K01")
        else:
            self.write("K11")

    def __getb2(self):
        """Get the b2 bit status."""
        return self.__b2

    def __setb2(self,value):
        """Set the b2 bit."""
        self.__b2=value
        if value==0:
            self.write("K02")
        else:
            self.write("K12")

    def __getc0(self):
        """Get the c0 bit status."""
        return self.__c0

    def __setc0(self,value):
        """Set the c0 bit."""
        self.__c0=value
        if value==0:
            self.write("K03")
        else:
            self.write("K13")

    def __getc1(self):
        """Get the c1 bit status."""
        return self.__c1

    def __setc1(self,value):
        """Set the c1 bit."""
        self.__c1=value
        if value==0:
            self.write("K04")
        else:
            self.write("K14")

    def __getc2(self):
        """Get the c2 bit status."""
        return self.__c2

    def __setc2(self,value):
        """Set the c2 bit."""
        self.__c2=value
        if value==0:
            self.write("K05")
        else:
            self.write("K15")
    
    #Public Properties
    ack=property(__get_ack,doc="DC590 i2c ack response")
    count=property(__get_count,doc="DC590 count")
    device_index=property(__get_device_index,__set_device_index,doc="DC590 Device Index")
    port_list=property(__get_port_list,doc="DC590 Port List")
    port=property(__get_port,doc="DC590 Port")
    b0=property(__getb0,__setb0,doc="DC590 B0 Bit.")
    b1=property(__getb1,__setb1,doc="DC590 B1 Bit.")
    b2=property(__getb2,__setb2,doc="DC590 B2 Bit.")
    c0=property(__getc0,__setc0,doc="DC590 C0 Bit.")
    c1=property(__getc1,__setc1,doc="DC590 C1 Bit.")
    c2=property(__getc2,__setc2,doc="DC590 C2 Bit.")
    
    #Public Methods
    
    def aux_i2c_mode(self):
        """Change the DC590 to Auxilary I2C mode."""
        self.write("MX")

    def board_id(self):
        """Read board ID and firmware""" 
        self.write("I")
        c=self.read(50)
        s=c[:c.rfind("\n")]
        return s

    def close_connection(self):
        """Close the DC590 Connection."""
        if self.__connected==True:
            try:
                self.__sp.close()
            except serial.SerialException:
                if self.__show_errors: print "Error closing COM%s." % comport
            finally:
                self.__connected=False

    def controller_id(self):
        """Read DC590 ID and firmware""" 
        self.write("i")
        c=self.read(50)
        s=c[:c.rfind("\n")]
        return s
    
    def hex_to_int(self,hex_string,default=0):
        """Convert hex string to integer"""   
        try:
            i=int(hex_string,16)
        except ValueError:
            i=default
            if self.__show_errors: print "Error converting hex data %s to integer." % hex_string
        finally:
            return i

    def i2c_mode(self):
        """Change the DC590 to I2C mode."""
        self.write("MI")
      
    def i2c_read_string_buffer(self,address=0,byte_count=1):
        """i2c read buffer: start,address+r,byte_count*data,stop"""
        s="s"                                            #add start bit
        s+="S"+self.int_to_hex(address | 0x01,2)         #add address, r
        for i in range(byte_count-1):
            s+="Q"                                         #add read command with ACK
        s+="R"                                           #add read command with NACK
        s+="p"                                           #add stop bit
        self.write(s)                                    #send the command
        r=self.__smbus_read_result()                     #read result and update ACK status
        return r                                         #return the string buffer
    
    def i2c_write_buffer(self,address=0,data_buffer=[0]):
        """I2c write buffer: start,address+w,buffer,stop"""
        s="s"                                            #start bit
        s+="S"+self.int_to_hex(address & 0xFE,2)         #add shifted address, WR bit set to 0
        for i in range(len(data_buffer)):
            s+="S"+self.int_to_hex(data_buffer[i],2)       #add the data byte  
        s+="p"                                           #add the stop bit   
        self.write(s)                                    #send the command
        self.__smbus_read_result()                       #set ACK status

    def identify(self):
        """Blink the LED on i/o pin C2"""
        for i in range(2):
            dc590.c2=0 #turn on LED on pin C2
            sleep(0.5)
            dc590.c2=1 #turn off LED on pin C2
            sleep(0.5)
        
    def int_to_hex(self,data=0,digit_count=2):
        """Convert int to hex string with digit_count digits."""
        try:
            s="%X" % data                                  
        except TypeError:
            s=""
            if self.__show_errors: print"Error converting '%s' to hex." % data
        finally:
            #pad leading 0's
            if (len(s)<digit_count):
                for i in range(digit_count-len(s)):
                    s='0'+s
            return s
      
    def iso_off(self):
        """Turn on the isolated power."""
        self.write("o")
      
    def iso_on(self):
        """Turn on the isolated power."""
        self.write("O")
      
    def ping(self):
        self.write("P")
        s=self.read()
        return s    
      
    def read(self,count=20):
        """read a string from the DC590"""
        s=""
        if self.__connected:
            try:
                s=self.__sp.read(count)
            except serial.SerialException:
                if self.__show_errors: print "Error reading string: %s from DC590." % s
        else:    
            if self.__show_errors: print "Read Error: Connection Not Open."       
        return s
      
    def __open_new_connection(self):
        """Open a serial connection"""
        if self.__count!=0:
            self.__port=self.__port_list[self.__device_index]
        try:
            self.__sp=serial.Serial(self.__port,timeout=self.__timeout)
        except serial.SerialException:
            if self.__show_errors: print "Cannot open COM%s." % comport
            self.__connected=False
        else:
            self.__sp.baudrate=self.__baudrate
            if self.__Linduino:
                #Flush the hello string from Linduino
                sleep(2)
                self.__sp.flushInput()
            self.__connected=True

    def read_LTC24XX_24bit(self,output_data):
        """Read normalized data from a LTC24XX device with 24 bit transaction"""
        command="xLT"+self.int_to_hex(output_data)+"RRX"
        self.write(command)
        s=self.read()
        #check for 3 bytes returned
        if len(s)==6:
            d=int(s,16)               #convert to integer
            sig=d & 0x200000          #check the sign bit
            d=(d & 0xDFFFFF)<<3       #set sign bit to 0 then align data
            if sig==0:
                d=-1*(16777216-d)       #convert from 2's complement data
        else:
            d=0
            if self.__show_errors: print "LTC24XX Read Error"
        f=float(d)/(8388608)       #normalize to -1 to +1 and convert to float
        return f
    
    def read_LTC24XX_32bit(self,output_data):
        """Read normalized data from a LTC24XX device with 32 bit transaction"""
        command="xLT"+self.int_to_hex(output_data)+"RRRX"
        self.write(command)
        s=self.read(8)
        #check for 4 bytes returned
        if len(s)==8:
            d=int(s,16)               #convert to integer
            sig=d & 0x20000000        #check the sign bit
            d=(d & 0xDFFFFFFF)<<3     #set sign bit to 0 then align data
            if sig==0:
                d=-1*(4294967296-d)     #convert from 2's complement data
        else:
            d=0
            if self.__show_errors: print "LTC24XX Read Error"
        f=float(d)/(2147483648)     #normalize to -1 to +1 and convert to float
        return f
        
    def scan(self):
        """Scan for available DC590's."""
        self.__count=0
        self.__port=0
        self.__port_list=[]
        self.__connected=False
        #scan through all ports looking for a DC590
        for port in range(256):
            try:
                s = serial.Serial(port,timeout=self.__timeout)
            except serial.SerialException:
                pass
            else:
                #port exists, send a id command
                s.baudrate=self.__baudrate
                if self.__Linduino:
                    s.timeout=2
                    s.write("\n") #ping the serial port for Linduino
                    c=s.read(5)   #read the hello string
                s.write("i\n")
                c=s.read(50)
                if len(c)!=0:
                    #got a response, strip end characters and look for DC590 string
                    c=c[:c.rfind("\n")]
                    if "DC590" in c:
                        #DC590 found increment the count and place the port in the list
                        self.__count=self.__count+1
                        self.__port_list.append(port)
                s.close()   
        if self.__count!=0:
            #set the current port to the first one found
            self.__port=self.__port_list[0]
            self.__open_new_connection()

    def __smbus_read_result(self):
        """SMBUS read result: get the result of an smbus read or write and check for ACK """
        data_string=self.read()                          #read the result from the DC590
        if data_string.find("N")!=-1:                    #check for N (not acknowlege)
            if self.__show_errors: print "Subordinate did not acknowledge"
            self.__ack=False
        else:
            self.__ack=True
        return data_string
            
    def smbus_read_string_buffer(self,address=0,command=0,byte_count=1):
        """SMBUS read string buffer: start,address+w,command,start,address+r,byte_count*data,stop"""
        s="s"                                            #add start bit
        s+="S"+self.int_to_hex(address & 0xFE,2)         #add address, w
        s+="S"+self.int_to_hex(command,2)                #add the command byte
        s+="s"                                           #add repeated start
        s+="S"+self.int_to_hex(address | 0x01,2)         #add address, r
        for i in range(byte_count-1):
            s+="Q"                                         #add read command with ACK
        s+="R"                                           #add read command with NACK
        s+="p"                                           #add stop bit
        self.write(s)                                    #send the command
        r=self.__smbus_read_result()                     #read result and check ACK status
        return r                                         #return the data string

    def smbus_read_byte_buffer(self,address=0,command=0,byte_count=1):
        """SMBUS read byte buffer: start,address+w,command,start,address+r,byte_count*data,stop"""
        data_string=self.smbus_read_string_buffer(address,command,byte_count)   #execute smbus read
        byte_buffer=[]
        if self.__ack:
            byte_buffer=self.__string_buffer_to_byte_buffer(data_string)
        return byte_buffer
    
    def smbus_read_byte(self,address=0,command=0):
        """SMBUS read byte: start,address+w,command,start,address+r,data_byte,stop"""
        data_string=self.smbus_read_string_buffer(address,command,1)   #execute 1 byte smbus read
        if self.__ack:
            data=self.hex_to_int(data_string)              #convert the data string to integer
        else:
            return 0                                       #return 0 if NACK                    

    def smbus_read_word(self,address=0,command=0):
        """SMBUS read byte: start,address+w,command,start,address+r,data_word,stop"""
        data_string=self.smbus_read_string_buffer(address,command,2)   #execute 2 byte smbus read
        if self.__ack:
            data=self.hex_to_int(data_string)              #convert the data string to integer
        else:
            return 0                                       #return 0 if NACK 

    def smbus_write_buffer(self,address=0,command=0,data_buffer=[0]):
        """SMBUS write buffer: start,address+w,buffer,stop"""
        s="s"                                            #start bit
        s+="S"+self.int_to_hex(address & 0xFE,2)         #add shifted address, WR bit set to 0
        s+="S"+self.int_to_hex(command,2)                #add the command byte
        for i in range(len(data_buffer)):
            s+="S"+self.int_to_hex(data_buffer[i],2)       #add the data byte  
        s+="p"                                           #add the stop bit   
        self.write(s)                                    #send the command
        self.__smbus_read_result()                       #set ACK status
    
    def smbus_write_byte(self,address=0,command=0,data_byte=0):
        """SMBUS write byte: start,address+w,byte,stop"""
        s="s"                                            #start bit
        s+="S"+self.int_to_hex(address & 0xFE,2)         #add shifted address, WR bit set to 0
        s+="S"+self.int_to_hex(command,2)                #add the command byte
        s+="S"+self.int_to_hex(data_byte,2)              #add the data byte  
        s+="p"                                           #add the stop bit   
        self.write(s)                                    #send the command
        self.__smbus_read_result()                       #set ACK status

    def smbus_write_word(self,address=0,command=0,data_word=0,order=msb_first):
        """SMBUS Write Word: start,address+w,high byte,low byte,stop"""
        s="s"                                            #start bit
        s+="S"+self.int_to_hex(address & 0xFE,2)         #add shifted address, WR bit set to 0
        s+="S"+self.int_to_hex(command,2)                #add the command byte
        d=self.int_to_hex(data_word,4)                   #convert the data word to hex
        if order==msb_first:
            s+="S"+d[0:2]                                  #add the high byte
            s+="S"+d[2:5]                                  #add the low byte
        else:
            s+="S"+d[2:5]                                  #add the low byte
            s+="S"+d[0:2]                                  #add the high byte  
        s+="p"                                           #add the stop bit   
        self.write(s)                                    #send the command
        self.__smbus_read_result()                       #set ACK status
      
    def spi_mode(self):
        """Change the DC590 to SPI mode."""
        self.write("MS")

    def spi_read_string_buffer(self,output_buffer=[0],byte_count=1):
        """SPI read string buffer: CS low,write output byte/read input string,CS High"""
        s="x"                                            #add CS low
        for i in range(byte_count):
            if i>=len(output_buffer):                      #check length of output buffer
                s+="R"                                       #if no more output, and read command
            else:
                s+="T"+self.int_to_hex(output_buffer[i],2)   #otherwise add SDO data byte
        s+="X"                                           #add CS high
        self.write(s)                                    #send the command
        input_string=self.read()                         #read the result from the DC590
        return input_string

    def spi_read_byte_buffer(self,output_buffer=[0],byte_count=1):
        """SPI read string buffer: CS low,write output byte/read input byte,CS High"""
        input_string=self.spi_read_string_buffer(output_buffer,byte_count)
        byte_buffer=self.__string_buffer_to_byte_buffer(input_string)
        return byte_buffer
    
    def spi_write_byte(self,command=0,data_byte=0):
        """SPI write byte: CS low, command,data, CS high"""
        s="x"                                            #add CS low
        s+="S"+self.int_to_hex(command,2)                #add the command byte    
        s+="S"+self.int_to_hex(data_byte,2)              #add data byte
        s+="X"                                           #add CS high
        self.write(s)                                    #send the command

    def spi_write_word(self,command=0,data_word=0,order=msb_first):
        """SPI write word: CS low, command,data, CS high"""
        s="x"                                            #add CS low
        s+="S"+self.int_to_hex(command,2)                #add the command byte    
        d=self.int_to_hex(data_word,4)                   #convert the data word to hex
        if order==msb_first:
            s+="S"+d[0:2]                                  #add the high byte
            s+="S"+d[2:5]                                  #add the low byte
        else:
            s+="S"+d[2:5]                                  #add the low byte
            s+="S"+d[0:2]                                  #add the high byte
        s+="X"                                           #add CS high
        self.write(s)                                    #send the command
          
    def spi_write_buffer(self,data_buffer=[0]):
        """SPI write buffer: CS low,data bytes,CS High"""
        s="x"                                            #add CS low
        for i in range(len(data_buffer)):
            s+="S"+self.int_to_hex(data_buffer[i],2)       #add data byte
        s+="X"                                           #add CS high
        self.write(s)                                    #send the command

    def __string_buffer_to_byte_buffer(self,string_buffer=[0]):
        """string buffer to byte buffer: Convert HEX character string to byte array"""
        byte_buffer=[]
        for i in range(len(string_buffer)/2):
            index=i*2
            x=self.hex_to_int(string_buffer[index:index+2])#convert each 2 hex characters to a byte
            byte_buffer.append(x)                          #convert the data string to integer
        return byte_buffer                               #return byte data buffer 

    def write(self,s):
        """write a string to the DC590"""
        if self.__connected:
            try:
                s+="\n"
                self.__sp.write(s)
            except serial.SerialException:
                if self.__show_errors: print "Error writing string: %s to DC590." % s
        else:    
           if self.__show_errors: print "Write Error: Connection Not Open."
      
if __name__=='__main__':
    print "Searching For DC590..."
    dc590=DC590_CLASS()                               
    print "DC590 count= %d" % dc590.count
    for i in range(dc590.count):
        print "dc590[%d] on COM%d" % (i,dc590.port_list[i]+1)
