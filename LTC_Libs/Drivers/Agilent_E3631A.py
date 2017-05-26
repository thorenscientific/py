################################################################################
#
# Agilent E3631A Triple Power Supply Driver
#
# Author:Robert Reay
#
# Description:
#   This is a GPIB driver for the Agilent E3631A triple power supply using
# the SCPI Instrument class. Supply Index: P5V=1, P25V=2, N25V=3
#
# Revision History:
#   1-5-2013: Robert Reay
#     Modify to use the SCPI_Instrument class
#   11-20-2011: Robert Reay
#     Initial code
#
################################################################################

from SCPI_Instrument import *

class AGILENT_E3631A(SCPI_Instrument):
    """Agilent E3631A Power Supply Driver"""

    def __init__(self,model="E3631A",address="GPIB0::5",debug=False):
        """Agilent E3631A constructor"""
        SCPI_Instrument.__init__(self,model,address,debug)
        self.__supply_names=['P6V','P25V','N25V']

    def apply(self,supply_index=1,voltage=5,current=5):
        """Update the selected supply's voltage and current immediately."""
        command='APPLY %s,%2.3f,%2.3f' % (self.__supply_names[supply_index-1],voltage,current)
        self.write(command)

    def __execute_command(self,command=None,use_query=False):
        """Execute a command"""
        if use_query:
            return self.query(command)
        else:
            self.write(command)
          
    def configure(self,number,vval,ival):
        """Update the selected supply's voltage and current without trigger."""
        command='INST:NSEL %d' % (number)
        self.__execute_command(command)
        command='VOLT:TRIG %f' % (vval)
        self.__execute_command(command)
        command='CURR:TRIG %f' % (ival)
        self.__execute_command(command)
      
    def couple_all(self):
        """Couple the trigger for all supplies."""
        self.__execute_command('INST:COUP ALL')

    def couple_none(self):
        """Uncouple the trigger for the supplies."""
        self.__execute_command('INST:COUP NONE');

    def measure_current(self,supply_index=1):
        """Measure current on the selected channel."""     
        command='MEAS:CURR? '+self.__supply_names[supply_index-1]
        return self.__execute_command(command,True)

    def measure_voltage(self,supply_index=1):
        """Measure voltage on the selected channel."""     
        command='MEAS:VOLT? '+self.__supply_names[supply_index-1]
        return self.__execute_command(command,True)

    def output_off(self):
        """Turn the output off."""
        self.__execute_command('OUTP OFF')

    def output_on(self):
        self.__execute_command('OUTP ON')
      
    def tracking_on(self):
        """Set the P25 & N25 Tracking on."""
        self.__execute_command('OUTP:TRAC ON')

    def tracking_off(self):
        """Set the P25 & N25 Tracking off."""
        self.__execute_command('OUTP:TRAC OFF')

    def trigger_bus(self):
        """Set the trigger to immediate."""
        self.__execute_command('TRIG:SOUR BUS')

    def trigger_immediate(self):
        """Set the trigger to immediate."""
        self.__execute_command('TRIG:SOUR IMM')
        
if __name__=='__main__':
    print "Searching for Agilent E3631A"
    ps=AGILENT_E3631A(debug=False)
    if ps.connected:
        print "Found "+ps.identify()+" at address %s" % (ps.address)
        ps.reset()                 
    else:
        print 'Power Supply Not Found'

