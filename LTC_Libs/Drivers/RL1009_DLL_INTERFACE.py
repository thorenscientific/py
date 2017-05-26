################################################################################
#
# RL1009_DLL_INTERFACE
#
# Author:Robert Reay
#
# Description:
#   This file contains an interface to the RL1009 USB to GPIB module used to
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

from ctypes import *

class RL1009(object):
    """RL1009 USB to GPIB DLL Interface."""

    #Class constructor & Private Methods

    def __init__(self,address=None,rlib=None):
        """RL1009 Constructor"""
        if rlib is None:
            self.__rlib=windll.REAY_LABS_GPIB
        else:
            self.__rlib=rlib
            self.set_terminator()
            self.set_timeouts()
        if address==None:
            self.__address=0
            self.__get_address()
        else:
            self.__address=address
            self.__set_address(self.__address)    

    def __del__(self):
        self.close_connection()

    def __get_address(self):
        """Returns the current GPIB address."""
        #public static extern byte get_address()
        self.__rlib.get_address.argtypes=[]
        self.__rlib.get_address.restype=c_byte
        if self.connected():
            self.__address=self.__rlib.get_address()
        return self.__address

    def __set_address(self,address):
        """Set the GPIB address."""
        #public static extern void set_address(byte address)
        self.__rlib.set_address.argtypes=[c_byte]
        self.__rlib.set_address.restype=None
        self.__address=address
        self.__rlib.set_address(self.__address)

    def __update_address(self,address):
        """Update the GPIB Address."""
        if address!=None:
            self.__address=address
            self.__set_address(self.__address)

    #Class methods
    
    def close_connection(self):
        """Close the USB Connection. Call before program termination."""
        # public static extern void close_connection()
        self.__rlib.close_connection.argtypes=[]
        self.__rlib.close_connection.restype=None
        return self.__rlib.close_connection()

    def clear_error(self):
        """Clear RL1009 error flag"""
        # public static extern void clear_error()
        self.__rlib.close_connection.argtypes=[]
        self.__rlib.close_connection.restype=None
        return self.__rlib.clear_error()

    def connected(self):
        """Returns the RL1009 connection status."""
        # public static extern bool connected()
        self.__rlib.connected.argtypes=[]
        self.__rlib.connected.restype=c_byte
        return self.__rlib.connected()

    def gpib_error(self):
        """Returns the RL1009 error flag status."""
        # public static extern bool gpib_error()
        self.__rlib.gpib_error.argtypes=[]
        self.__rlib.gpib_error.restype=c_byte
        return self.__rlib.gpib_error()

    def error_description(self):
        """Returns a text description of the current error."""
        # public static extern string error_description()
        self.__rlib.error_description.argtypes=[]
        self.__rlib.error_description.restype=c_char_p
        return self.__rlib.error_description()

    def device_clear(self,address=None):
        """Execute a GPIB device clear command."""
        #public static extern void device_clear(byte address)
        self.__rlib.device_clear.argtypes=[c_byte]
        self.__rlib.device_clear.restype=None
        self.__update_address(address) 
        return self.__rlib.device_clear(self.__address)

    def get_timeouts(self):
        """ Returns the GPIB read and write timeout values in ms."""
        # public static extern byte get_timeouts(ref int read_timeout, ref int write_timeout)
        r=c_int()
        w=c_int()
        #self.__rlib.get_timeouts.argtypes=[]
        self.__rlib.get_timeouts.restype=c_int
        self.__rlib.get_timeouts(byref(r),byref(w))
        return [r.value, w.value]

    def get_terminator(self):
        """Returns the GPIB terminator index."""
        #public static extern byte get_terminator()
        #Values: 0=none,1=line feed(0x0A),2=carriage return(0x0D),3=crlf(0x0D0A)
        self.__rlib.get_terminator.argtypes=[]
        self.__rlib.get_terminator.restype=c_byte
        return self.__rlib.get_terminator()

    def group_trigger(self,address_list):
        """Executes a GPIB group trigger for the given address list."""
        #public static extern void group_trigger(string address_list)
        self.__rlib.group_trigger.argtypes=[c_char_p]
        self.__rlib.group_trigger.restype=None
        return self.__rlib.group_trigger(address_list)
    
    def local(self,address=None):
        """Force the GPIB device into local mode."""
        #public static extern void local(byte address)
        self.__rlib.local.argtypes=[c_byte]
        self.__rlib.local.restype=None
        self.__update_address(address)
        return self.__rlib.local(self.__address)

    def query(self,command,address=None):
        """Execute a GPIB write then read command."""
        #public static extern string query(byte address, string command)
        self.__rlib.query.argtypes=[c_byte,c_char_p]
        self.__rlib.query.restype=c_char_p
        self.__update_address(address)
        return self.__rlib.query(self.__address, command)

    def read(self,address=None):
        """Execute a GPIB read."""
        #public static extern string read(byte address)
        self.__rlib.read.argtypes=[c_byte]
        self.__rlib.read.restype=c_char_p
        self.__update_address(address) 
        return self.__rlib.read(self.__address)

    def serial_poll(self,address=None):
        """Returns the result of a GPIB poll command."""
        #public static extern byte serial_poll(byte address)
        self.__rlib.serial_poll.argtypes=[c_byte]
        self.__rlib.serial_poll.restype=c_byte
        self.__update_address(address) 
        return self.__rlib.serial_poll(self.__address)

    def set_led_green(self):
        """Set the RL1009 status led green."""
        #public static extern void set_led_green()
        self.__rlib.set_led_green.argtypes=[]
        self.__rlib.set_led_green.restype=None
        return self.__rlib.set_led_green()

    def set_led_off(self):
        """Turn the RL1009 status led off."""
        #public static extern void set_led_off()
        self.__rlib.set_led_off.argtypes=[]
        self.__rlib.set_led_off.restype=None
        return self.__rlib.set_led_off()

    def set_led_red(self):
        """Set the RL1009 status led red."""
        #public static extern void set_led_red()
        self.__rlib.set_led_red.argtypes=[]
        self.__rlib.set_led_red.restype=None
        return self.__rlib.set_led_red()

    def set_terminator(self,terminator=1):
        """Set the GPIB termination character index."""       
        #public static extern void set_terminator(byte terminator);
        #Values: 0=none,1=line feed(0x0A),2=carriage return(0x0D),3=crlf(0x0D0A)
        self.__rlib.set_terminator.argtypes=[c_byte]
        self.__rlib.set_terminator.restype=None
        return self.__rlib.set_terminator(terminator)

    def set_timeouts(self,read_timeout=2000, write_timeout=100):
        """Set GPIB read and write timeouts in ms."""
        #public static extern void set_timeouts(int read_timeout, int write_timeout);
        self.__rlib.set_timeouts.argtypes=[c_long,c_long]
        self.__rlib.set_timeouts.restype=None
        return self.__rlib.set_timeouts(read_timeout, write_timeout)

    def srq_asserted(self):
        """Return the SRQ line state."""
        #public static extern bool srq_asserted();
        self.__rlib.srq_asserted.argtypes=[]
        self.__rlib.srq_asserted.restype=c_byte
        return self.__rlib.srq_asserted()

    def system_error(self,address=None):
        self.__update_address(address)
        return self.query("SYST:ERROR?")
    
    def version(self):
        """Returns the RL1009 version information."""
        #public static extern string version();
        self.__rlib.version.argtypes=[]
        self.__rlib.version.restype=c_char_p
        return self.__rlib.version()

    def write(self,command,address=None):
        """Execute a GPIB write command"""
        #public static extern void write(byte address, string command);
        self.__rlib.write.argtypes=[c_byte,c_char_p]
        self.__rlib.write.restype=None
        self.__update_address(address)
        return self.__rlib.write(self.__address, command)

    #Properties
    address=property(fget=__get_address,fset=__set_address,doc="GPIB Address")

if __name__=='__main__':
    r=RL1009(9)
    if r.connected():
        print "RL1009 connected"
    else:
        print "RL1009 not found"
