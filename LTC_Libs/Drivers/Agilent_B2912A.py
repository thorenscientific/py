################################################################################
#
# Agilent B2912AA Precision Source/Measurement Unit Device Driver
#
# Author:Robert Reay
#
# Description:
#   This file is a driver for the Agilent B2912A Dual V/I meter. This driver
#   still needs a lot of work.
#
# Revision History:
#   1-6-2012 : Robert Reay
#     Modify code for SCPI class.
#   9-175-2012: Robert Reay
#     Initial code
#
################################################################################

from SCPI_Instrument import *


class AGILENT_B2912A(SCPI_Instrument):
    """Agilent B2912A Data Aquisition Driver"""

    def __init__(self,model="B2912A",address="GPIB0::23",debug=True):
        """Agilent B2912A constructor"""
        SCPI_Instrument.__init__(self,model,address,debug)
        self.__debug=debug
      
    def __execute_command(self,prefix=":OUTP",function=None,channel=1,value=None,use_query=False):
        """Execute a command"""
        command=prefix
        if channel==2:
            command+="2"
        if function!=None:
            command+=str(function)
        if value!=None:
            comand+=" "+str(value)
        if self.__debug:
            print command
        if use_query:
            return self.query(command)
        else:
            self.write(command)

    def output_off(self,channel=1):
        """Turn the channel of"""
        self.__execute_command(":OUTP",None,channel,"OFF",False)
          
    def output_on(self,channel=1):
        """Turn the channel on"""
        self.__execute_command(":OUTP",None,channel,"ON",False)

    def set_voltage(self,channel=1,value=0):
        """Setup the vi voltage value immediately"""
        value=str(value)
        if channel==1:
            self.write(":SOUR:VOLT "+value)
        else:
            self.write(":SOUR2:VOLT "+value)
          
    def setup_source_voltage(self,channel=1,v_range=0):
        """Setup the vi to source voltage and set the range"""
        if channel==1:
            self.write(":SOUR:FUNC:MODE:VOLT")
            if v_range==0:
                self.write(":SOUR:VOLT:RANG:AUTO ON")
            else:
                self.write(":SOUR:VOLT:RANG:AUTO OFF")
                v_range=str(v_range)
                self.write(":SOUR:VOLT:RANG "+v_range)
        else:
            self.write(":SOUR2:FUNC:MODE:VOLT")
            if v_range==0:
                self.write(":SOUR2:VOLT:RANG:AUTO ON")
            else:
                self.write(":SOUR2:VOLT:RANG:AUTO OFF")
                v_range=str(v_range)
                self.write(":SOUR2:VOLT:RANG "+v_range)
          
if __name__=='__main__':
    print "Searching for Agilent B2912A"
    vi=AGILENT_B2912A()
    if vi.connected:
        print "Found "+vi.identify()+" at address %s" % (vi.address)
    else:
        print 'B2912A Not Found'
