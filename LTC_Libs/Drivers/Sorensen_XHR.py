################################################################################
#
# Sorensen XHR Power Supply
#
# Author:Robert Reay
#
# Description:
#   This file is the driver for the Sorensen XHR 1kW power supply. The command
#   set is not SCPI compliant.
#
# Revision History:
#   1-5-2013: Robert Reay
#     Modify using the General_Instrument class.
#   9-28-2012: Robert Reay
#     Initial code
#
################################################################################

from General_Instrument import *      

class SORENSEN_XHR(General_Instrument):
    """Sorensen XHR Driver"""
    
    def __init__(self,model="XHR20-50",address="GPIB0::3",debug=False):
        """Constructor."""
        General_Instrument.__init__(self,model,address,debug)

    def __execute_command(self,function="ID?",value=None):
        """Execute the a command"""
        command=str(function)
        if value!=None:
            command+=" "+str(value)
        if command.find("?")!=-1:
            self.write(command)
            return self.read()
        else:
            self.write(command)

    def apply(self,voltage=0,current=0):
        """Apply Voltage and Current """
        command="VSET "+str(voltage)
        command+=";ISET "+str(current)
        self.__execute_command(command)

    def error(self):
        """Return the error"""
        return self.__execute_command("ERR?")
    
    def identify(self):
        """Identify the instrument"""
        #Overide the identify method with the new command
        return self.__execute_command("ID?")
    
    def measure_current(self):
        """Measure Current"""
        return self.__execute_command("IOUT?")

    def measure_voltage(self):
        """Measure Voltage"""
        return self.__execute_command("VOUT?")

    def output_on(self):
        """Turn output on"""
        self.__execute_command("OUT ON")

    def output_off(self):
        """Turn output off"""
        self.__execute_command("OUT OFF")
        
    def over_voltage(self,voltage=10):
        """Set the over-voltage trip point"""
        command="OVSET "+str(voltage)
        self.__execute_command(command)
    
    def reset(self):
        """Reset the instrument"""
        self.__execute_command("CLR")
        self.output_off()

if __name__=='__main__':
    print "Searching for XHR20-50"
    ps=SORENSEN_XHR(debug=False) 
    if ps.connected:             
        print "Found "+ps.identify()+" at address %s" % (ps.address)
    else:
        print "Power Supply Not Connected"
    
