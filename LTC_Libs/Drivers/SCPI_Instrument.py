################################################################################
#
# SCPI_Instrument
#
# Author:Robert Reay
#
# Description:
#   This file contains an class for instruments that implement the SCPI
#   scripting language. Almost all Agilent instruments implement SCPI. The class
#   is based on the General_Instrument class and forms the ancestor for most
#   Agilent device drivers.
#
# Revision History:
#   1-5-2012:Robert Reay
#     Initial code
#
################################################################################

from General_Instrument import *

class SCPI_Instrument(General_Instrument):
    """SCPI Instrument Base Class"""
    
    def beep(self):
        """Send a beep command."""
        self.write("SYST:BEEP")
      
    def clear_status(self):
        """Send the *CLS command."""
        self.write("*CLS")

    def display_clear(self):
        self.write("DISP:TEXT:CLE")  

    def display_off(self):
        """Turn the display off"""
        self.write('DISP OFF')
          
    def display_on(self):
        """Turn the display on"""
        self.write('DISP ON')

    def display_text(self,text=""):
        """Display Text"""      
        command="DISP:TEXT '"+text+"'"
        self.write(command)
      
    def enable_serial_polling(self):
        """Enable the instrument to report operation complete via serial polling"""
        self.clear_status()     #clear the stauts register
        self.write("*ESE 1")    #enable the operation complete bit in the event register
        self.write("*SRE 32")   #enable the event register to update the status register
      
    def error(self):
        """Get error message."""
        return self.query("SYST:ERROR?")

    def fetch(self):
        """Send FETCH? query."""
        return self.query("FETCH?")
   
    def identify(self):
        """Identify the Instrument"""
        return self.query("*IDN?")

    def init(self):
        """Send INIT command."""
        self.write("INIT")

    def __init__(self,model="34401A",address=None,debug=False):
        """SCPI Instrument Constructor."""
        General_Instrument.__init__(self,model,address,debug=debug)
    
    def initiate_measurement(self,enable_polling=False):
        """Initiate a measurement"""
        if enable_polling:
            self.enable_serial_polling()  #enable serial polling
            self.clear_status()           #clear the status register     
            self.query("*OPC?")           #wait until previous operation is complete
            self.write("INIT")            #arm the trigger
            self.write("*OPC")            #enable operation complete update to the status register
        else:
            self.query("*OPC?")           #wait until previous operation is complete
            self.write("INIT")            #arm the trigger          
      
    def read_measurement(self):
        """Send FETCH? query."""
        return self.query("FETCH?")

    def ready(self):
        """Return True is the instrument is ready for command."""
        return self.connected

    def reset(self):
        """Send the *RST command."""
        self.write("*RST")
            
    def trigger(self):
        """Send the *TRG command."""
        self.write('*TRG')
 
if __name__=='__main__':
    model="34401A"
    address="GPIB0::22"
    print "Searching for "+model
    dvm=SCPI_Instrument(model,address,debug=False)
    if dvm.connected:
        print "Found "+dvm.identify()+" at address %s" % (dvm.address)
    else:
        print "Agilent 34401A not found"
    
