################################################################################
#
# RL1009_SERIAL_CLASS
#
# Author:Robert Reay
#
# Description:
#   This file contains a serial interface to the RL1009 USB to GPIB module used to
# control GPIB instruments. Before running this program, the RL1009_Setup.exe 
# installer must be run. It can be found at http://www.reaylabs.com/software.html.
# The installer will place the REAY_LABS_GPIB.dll into the system directory. See
# the RL1009_USB_to_GPIB.chm help file for a more detailed explanation of each
# function.
#
#   See the RL1009_CLASS_TEST.py for a full test routine.
#
# Revision History:
#   9-17-2012:Robert Reay
#     Move the identify command to the GPIB instrument class.
#   11-20-2011:Robert Reay
#     Initial code
#
################################################################################

import serial

#class RL1009:
###EDIT DJS force class to new-style to use properties
class RL1009(object):
    """RL1009 USB to GPIB Serial Driver Class."""
    #RL1009 constructor and private methods
    
    def __init__(self,comport=1,address=5):
        """RL1009 Class Constructor."""
        self.__error_list=[]
        self.__error=False
        ###EDIT DJS
        if (type(comport) == 'int'):
            self.port=comport-1
        else:
            self.port=comport
        ####
        self.address=address;
        try:
            self._sp=serial.Serial(self.port,timeout=5)
        except serial.SerialException:
            s="Cannot open COM%s" % comport
            self.__error_list.append(s)
            self.__error=True
            self.__connected=False
        else:
            self.__connected=True 
            self.set_led_green()
            self.set_address(self.address)
            if (self.version() != 'RL1009 USB<->GPIB VER 1.110\n'):
                raise Exception('Update RL1009 firmware to Version 1.110 to fix 5 second timeout bug.\n{}'.format(self.version()))
             
    def __update_error(self,return_code):
        """RL1009 Error Handler."""
        if return_code==1:
            s="RL1009 in sleep mode"
        elif return_code==2:
            s="GPIB data not accepted. Listener didn't release NDAC"
        elif return_code==3:
            s="GPIB not ready. NRFD signal held low."
        elif return_code==4:
            s="GPIB no listener."
        elif return_code==5:
            s="GPIB no data (read timeout)."
        elif return_code==7:
            s="GPIB DAC line timeout."
        elif return_code==8:
            s="Serial Read Communications Error"
        elif return_code==9:
            s="Serial Write Communications Error"
        elif return_code==10:
            s="Serial Read Timeout"
        elif return_code==11:
            s="Serial Write Timeout"
        else:
            s="Unknown Error"
        if return_code!=6:
            self.__error_list.append(s)
            self.__error=True

    def __read_char(self):
        """Read a character from the serial connection."""
        try:
            c=self._sp.read(1)
        except serial.SerialException:
            self.__update_error(8)
            c=chr(8)
        else:
            #if c is empty, a timeout occured
            if len(c)==0:
                c=chr(10)
        return c 

    def __read_error_code(self):
        """Read and process the RL1009 error code."""
        c=self.__read_char()
        return_code=ord(c)
        self.__update_error(return_code)
      
    def __read_string(self):
        """Read a string from the RL1009."""
        s=""
        if self.__connected==True:
            try:
                s=self._sp.readline()
            except serial.SerialException:
                self.__update_error(8)
            else:
                if len(s)==0:
                    self.__update_error(10)
                else:
                    self.__read_error_code()
        return s
    
    def __query_string(self,s):
      """Write then Read a string from the RL1009."""
      if self.__connected==True:
        s=s+"\n"
        try:
          self._sp.write(s)
        except serial.SerialException:
          self.__update_error(9)
        finally:
          s=self.__read_string()
          return s
        
    def __write_string(self,s):
        """Write a string to the RL1009."""
        if self.__connected==True:
            s=s+"\n"
            try:
                self._sp.write(s)
            except serial.SerialException:
                self.__update_error(9)

    #Private Property Interface Routines
          
    def __get_error(self):
        """Get the RL1009 error status."""
        return self.__error
    
    def __get_error_list(self):
        """Get the RL1009 error list."""
        return self.__error_list
    
    #Public Properties
    ###DJS properties don't work well in python2 unless class inherits from "object" to force new-style classes
    error=property(__get_error,doc="RL1009 Error Indicator")
    error_list=property(__get_error_list,doc="RL1009 Error List")

    #Public Functions
    
    def clear_errors(self):
        """Clear the RL1009 error list and error variable."""
        self.__error=False
        self.__error_list=[]
      
    def close_connection(self):
        """Close the RL1009 serial connection"""
        if self.__connected==True:
            self._sp.close()

    def connected(self):
        """Check Serial Connection"""
        return self.__connected

    def device_clear(self,address):
        """GPIB device clear"""
        if address!=self.address:
            self.address=address
            self.set_address(self.address)
        command="C"
        self.__write_string(command)
        self.__read_error_code()

    def error_description(self):
        """Get the description of the current error"""
        return self.error_list[0]
    
    def local(self):
        """For the GPIB device into local mode"""
        self.__write_string("L")
        self.__read_error_code()
      
    def get_address(self):
        """Get the RL1009 GPIB address"""
        self.__write_string("a")
        c=self.__read_char()
        c=c+self.__read_char()
        self.__read_error_code()
        return int(c)
    
    def get_timeouts(self):
        """Get the GPIB read and write timeouts in ms"""
        self.__write_string("t")
        read_timeout=""
        for i in range(5):
            read_timeout=read_timeout+self.__read_char()
        write_timeout=""
        for i in range(5):
            write_timeout=write_timeout+self.__read_char()
        self.__read_error_code()
        timeouts=[]
        timeouts.append(int(read_timeout))
        timeouts.append(int(write_timeout))
        return timeouts
    
    def group_trigger(self,address_list):
        """Group trigger the GPIB Bus"""
        command="G"+address_list
        self.__write_string(command)
        self.__read_error_code()
      
    def query(self,command):
        """Query the GPIB device"""
        cmd="Q"+command
        s=self.__query_string(cmd)
        return s
    
    def read(self):
        """Read a GPIB response"""
        s=self.__query_string("R")
        return s
    
    def serial_poll(self):
        """Execute a GPIB Serial Poll"""
        self.__write_string("S")
        c=self.__read_char()
        self.__read_error_code()
        code=ord(c)
        return code
    
    def set_address(self,address):
        """Set the RL1009 GPIB address"""
        if address<10:
            command="A0%d" % address
        else:
            command="A%d" % address
        self.__write_string(command)
        self.__read_error_code()
      
    def set_led_green(self):
        """Set the RL1009 Status LED to green"""
        self.__write_string("o")
        self.__read_error_code()

    def set_led_off(self):
        """Set the RL1009 Status LED to off"""
        self.__write_string("r")
        self.__read_error_code()
      
    def set_led_red(self):
        """Set the RL1009 Status LED to red"""
        self.__write_string("r")
        self.__read_error_code()

    def set_timeouts(self,read_timeout=2000, write_timeout=100):
        """Set the GPIB read and write timeouts in ms. Also update serial port timeout to match"""
        self._sp.timeout = max(read_timeout, write_timeout)/1000.0 + 1 #seconds
        timeout= '%05d%05d' % (read_timeout, write_timeout)
        command="T"+timeout
        self.__write_string(command)
        self.__read_error_code()    

    def srq_asserted(self):
        """Check the status of the GPIB SRQ line"""
        self.__write_string("s")
        c=self.__read_char()
        self.__read_error_code()
        code=ord(c)
        if code==0:
            srq=False
        else:
            srq=True
        return srq
    
    def version(self):
        """Get the RL1009 version"""
        s=self.__query_string("V")
        return s
    
    def write(self,command):   
        """Have the RL1009 write a GPIB command"""
        cmd="W"+command
        self.__write_string(cmd)
        self.__read_error_code()
      
if __name__=='__main__':
    r=RL1009(9)
    if r.connected():
        print "RL1009 connected"
    else:
        print "RL1009 not found"
