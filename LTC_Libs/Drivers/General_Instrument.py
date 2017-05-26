################################################################################
#
# General_Instrument
#
# Author:Robert Reay
#
# Description:
#   This file contains a generic instrument class with GPIB or USB
#   connectivity. It works with the RL1009 USB to GPIB Controller, and
#   the Agilent 82357A USB/GPIB Interface controller using the PyVisa
#   software package. USB connectivity is controlled using the PyVisa software only.
#
#   The connection is not complete until the model name of the instrument is found.
#   The address passed to the constructor will be searched first before a complete
#   search is started. The RL1009 will be searched first, the VISA device list second.
#
#   Addresses follow the VISA convention.
#   Examples:
#     "GPIB0::22"                         #address 22 on Agilent USB to GPIB
#     "RL1009:22"                         #address 22 on RL1009
#     "USBInstrument1"                    #first USB address in the VISA device list
#     "USBInstrument2"                    #second USB address in the VISA device list
#     "USB0::0x0957::0x17B4::MY52400124"  #specific USB address in the VISA device list
#
#   The actual USB or GPIB address can be found using the
#   Agilent Connection Expert program.
#
#   This class forms the ancestor for individual device drivers.
#
#   Revision History:
#     1-9-2013:Robert Reay
#       Added device_clear routine
#     1-5-2013:Robert Reay
#       Initial code
#
################################################################################

#Libraries Needed
from ctypes import *
from time import sleep
try:
    from RL1009_DLL_INTERFACE import *
except:
    RL1009_DLL_missing=True
else:
    RL1009_DLL_missing=False  
try:
    from visa import *
except:
    visa_missing=True
else:
    visa_missing=False

class General_Instrument():
    """General Instrument Base Class"""

    def __check_connections(self,address):
        """Check RL1009 or VISA connection"""
        self.__RL1009_ok=False
        self.__visa_ok=False
        if self.__check_RL1009_connection(address):
            self.__RL1009_ok=True
        else:
            if self.__check_visa_connection(address):
                self.__visa_ok=True
          
    def __check_RL1009_connection(self,address):
        """Check RL1009 connection"""
        if not RL1009_DLL_missing:
          if self.__RL1009==None:
            self.__RL1009=RL1009()
            if self.__RL1009.connected():
              if address!=None:
                if (type(address).__name__!='int'):
                  #address is a string,strip non digit characters
                  add=""
                  address=address.replace("RL1009","")
                  for i in range(len(address)):
                    if address[i].isdigit():
                      add+=address[i]
                  new_address=int(add)
                else:
                  #address is an integer
                  new_address=address
              else:
                new_address=0
              self.__RL1009.set_timeouts(3000,1000)
              self.__RL1009.address=new_address       
              if self.__ready():
                self.__address="RL1009::"+str(new_address)
                if self.__debug: print "Found %s at RL1009::%s" % (self.__id_string,new_address)
                return True
              else:
                #instrument model not found do a search
                start_search=True
                if address!=None:
                  if (type(address).__name__!='int'):
                    if (address.count("USB")==1): start_search=False
                if start_search:
                  if self.__search_RL1009():
                    if self.__debug: print "Found %s at RL1009::%s" % (self.__id_string,new_address)
                    return True
                  else:
                    if self.__debug: print "Can't find %s" % self.__model  
            else:
              if self.__debug: print "RL1009 Not Connected"
        else:
            if self.__debug: print "Missing RL1009 DLL"
        return False

    def __check_visa_connection(self,address):
        """Check visa connection"""    
        if not visa_missing:
            try:
                self.__visa=instrument(address)
            except:
                search_visa=True
            else:
                self.__visa.timeout=3
                self.__visa.termchar=LF
                self.__visa_ok=True
                if self.__ready():
                    self._address=address
                    if self.__debug: print "Found %s at %s" % (self.__id_string,self.__address)
                    return True
                else:
                    search_visa=True
            if search_visa:
                if self.__search_visa():
                    if self.__debug: print "Found %s at %s" % (self.__id_string,self.__address)
                    return True
                else:
                    if self.__debug: print "Can't find %s" % self.__model
                    self.__visa_ok=False
        else:
            if self.__debug: print "Missing VISA DLL"
        return False

    def __get_address(self):
        """Get connection address"""
        #Address property get function
        return self.__address
    
    def __get_connected(self):
        """Get connection status"""
        #Connected property get function
        if ((self.__RL1009_ok) | (self.__visa_ok)):
            return True
        else:
            return False

    def device_clear(self):
        """GPIB device clear"""
        if self.__debug: print "GPIB device clear"
        if self.__visa_ok:
            return self.__visa.clear()
        else:
            return self.__RL1009.device_clear()
        
    def identify(self):
        """Identify the Instrument"""
        #This routine will execute the SCPI identify command
        #If the child class in not SCPI compatible,then this
        #routine needs to be overriden with the appropriate
        #command
        return self.query("*IDN?")
    
    def __init__(self,model="",address=None,debug=False):
        """General_Instrument Class constructor"""
        self.__debug=debug
        self.__address=address
        self.__RL1009=None
        self.__id_string=""
        self.__model=model    
        self.__check_connections(address)

    def measurement_complete(self):
        """Check for a completed measurement using the serial poll command."""
        if self.__visa_ok:
            try:
                self.__visa.wait_for_srq(0.001)
            except:
                return False
            else:
                return True
        else:
            if self.__RL1009.serial_poll()==0:
                return False
            else:
                return True
        
    def query(self,command):
        """Instrument Query"""
        if self.__debug: print command
        if self.__visa_ok:
            return self.__visa.ask(command)
        else:
            return self.__RL1009.query(command)

    def read(self):
        """Instrument Read"""
        if self.__visa_ok:
            try:
                return self.__visa.read()
            except:
                return ''
        else:
          return self.__RL1009.read()
        
    def __ready(self):
        """Check that the connected instrument matches the model name."""
        self.__id_string=self.identify()
        if(self.__id_string.count(self.__model)==1):
            return True
        else:
            return False
      
    def __search_RL1009(self):
        """Search the RL1009 addresses for the instrument model name"""  
        if self.__debug: print "Searching RL1009 for "+self.__model        
        if self.__RL1009.connected()==True:
            self.__RL1009.set_timeouts(200,100)
            for address in range(32):
                self.__RL1009.address=address
                if self.__debug: print "RL1009::%d" % address
                if self.__ready():
                    self.__RL1009.set_timeouts(3000,1000)
                    self.__address="RL1009::"+str(address)
                    return True
        return False

    def __search_visa(self):
        """Search VISA list for the instrument model name"""
        self.__visa_ok=True
        if self.__debug: print "Searching VISA for "+self.__model
        try:
            instrument_list=get_instruments_list(True)
        except:
            return False
        for i in range(len(instrument_list)):
            self.__address=instrument_list[i]
            if self.__debug: print self.__address
            try:
                self.__visa=instrument(self.__address)
            except:
                pass
            else:
                if self.__ready():
                    self.__visa.timeout=3
                    self.__visa.termchar=LF
                    return True
        self.__visa_ok=False
        return False
    
    def set_timeouts(self,read_timeout=3000,write_timeout=1000):
        """Set the Read and Write timeouts in ms."""
        if self.__visa_ok:
            self.__visa.timeout=read_timeout/1000
        else:
            self.__RL1009.set_timeouts(read_timeout,write_timeout)

    def wait(self,time=1):
        """Wait for Seconds"""
        sleep(time)

    def write(self,command):
        """Write a command"""
        if self.__debug: print command
        if self.__visa_ok:
            self.__visa.write(command)  
        else:
            self.__RL1009.write(command)
      
    #Properties
    address=property(fget=__get_address,doc="connection address")
    connected=property(fget=__get_connected,doc="connection status")
 
if __name__=='__main__':
    gpib_model="34401A"
    usb_model="MSO-X 4034A"
    #gpib_address="RL1009::9"
    gpib_address="GPIB0::22"
    #gpib_address=9
    #usb_address="USB0::0x0957::0x17B4::MY52400124"
    usb_address="USBInstrument1"
    print "Searching for %s and %s" % (gpib_model,usb_model)
    gpib=General_Instrument(gpib_model,gpib_address,debug=False)
    usb=General_Instrument(usb_model,usb_address,debug=False)
    if gpib.connected:
        print "%s Ready" % gpib.identify()
    else:
        print "%s not found" % gpib_model
    if usb.connected:
        print "%s Ready" % usb.identify()
    else:
        print "%s not found" % usb_model
  
