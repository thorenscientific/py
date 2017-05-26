################################################################################
#
# Agilent 34401A 6.5 Digit Multimeter Device Driver
#
# Author:Robert Reay
#
# Description:
#   This file is a driver for the Agilent 34401A DVM based on the RL1009 USB to
# to GPIB controller. The calibration and Calculate commands are not implemented.
#
# The measure command automatically starts a measurement and waits for the result. Use
# the configure command to set up a measurement without starting it, then use the init()
# and fetch() commands to start and read the result.
#
# Revision History:
#   1-5-2013: Robert Reay
#     Modify to use the SCPI_Instrument class
#   9-25-2012: Robert Reay
#     Initial code
#
################################################################################

from SCPI_Instrument import *      

class AGILENT_3458A(General_Instrument):
    """Agilent 3458A DVM Driver"""
    
    def __init__(self,model="3458A",address="GPIB0::23",debug=False):
        """Agilent 3458A Constructor."""
        General_Instrument.__init__(self,model,address,debug=debug)

    def __execute_command(self,prefix="MEAS:",function="VOLT:DC",dvm_range=None,dvm_resolution=None,dvm_value=None,use_query=True):
        """Execute the dvm command"""
        command=str(prefix)+str(function)
        if use_query:
            command+="?"
        if ((dvm_range!=None) & (dvm_resolution!=None)):
            command+=" "+str(dvm_range)+","+str(dvm_resolution)
        if dvm_value!=None:
            command+=" "+str(dvm_value)
        if use_query:
            return self.query(command)
        else:
            self.write(command)
              
    #Configure Commands
    #nplc: number of power lines cycles to integrate during a measurement
    #aperature: the sample time in seconds for making a frequency or period measurement
           
    # def configure_ac_current(self,dvm_range=None,dvm_resolution=None):
        # """Configure AC Current"""
        # self.__execute_command("CONF:","CURR:AC",dvm_range,dvm_resolution,None,False)

    # def configure_ac_voltage(self,dvm_range=None,dvm_resolution=None):
        # """Configure AC Voltage"""
        # self.__execute_command("CONF:","VOLT:AC",dvm_range,dvm_resolution,None,False)

    # def configure_continuity(self):
        # """Configure Contiunity"""
        # self.__execute_command("CONF:","CONT",None,None,None,False)

    # def configure_diode(self):
        # """Configure Diode"""
        # self.__execute_command("CONF:","DIOD",None,None,None,False)

    # def configure_dc_current(self,dvm_range=None,dvm_resolution=None,nplc=None):
        # """Configure DC Current"""
        # self.__execute_command("CONF:","CURR:DC",dvm_range,dvm_resolution,None,False)
        # if nplc!=None:
            # self.__execute_command("SENS:","CURR:DC:NPLC",None,None,nplc,False) 
           
    def configure_dc_voltage(self,dvm_range=None,dvm_resolution=None,nplc=None):
        """Configure DC Voltage"""
        self.__execute_command("FUNC","DCV",dvm_range,dvm_resolution,None,False)
        if nplc!=None:
            self.__execute_command("SENS:","VOLT:DC:NPLC",None,None,nplc,False)               

    # def configure_four_wire_resistance(self,dvm_range=None,dvm_resolution=None,nplc=None):
        # """Configure 4 Wire Resistance"""
        # self.__execute_command("CONF:","FRES",dvm_range,dvm_resolution,None,False)
        # if nplc!=None:
            # self.__execute_command("SENS:","FRES:NPLC",None,None,nplc,False)

    # def configure_frequency(self,dvm_range=None,dvm_resolution=None,aperature=None):
        # """Configure Frequency"""
        # self.__execute_command("CONF:","FREQ",dvm_range,dvm_resolution,None,False)
        # if aperature!=None:
            # self.__execute_command("SENS:","FREQ:APER",None,None,aperature,False)

    # def configure_ratiometric_dc_voltage(self,dvm_range=None,dvm_resolution=None):
        # """Configure ratiometric DC Voltage (high/low)"""
        # self.__execute_command("CONF:","VOLT:DC:RAT",dvm_range,dvm_resolution,None,False)

    # def configure_resistance(self,dvm_range=None,dvm_resolution=None,nplc=None):
        # """Configure Resistance"""
        # self.__execute_command("CONF:","RES",dvm_range,dvm_resolution,None,False)
        # if nplc!=None:
            # self.__execute_command("SENS:","RES:NPLC",None,None,nplc,False)

    # def configure_period(self,dvm_range=None,dvm_resolution=None,aperature=None):
        # """Configure Period"""
        # self.__execute_command("CONF:","PER",dvm_range,dvm_resolution,None,False)
        # if aperature!=None:
            # self.__execute_command("SENS:","PER:APER",None,None,aperature,False)

    #Measure Commands
           
    # def measure_ac_current(self,dvm_range=None,dvm_resolution=None):
        # """Measure AC Current"""
        # return self.__execute_command("MEAS:","CURR:AC",dvm_range,dvm_resolution,None,True)

    # def measure_ac_voltage(self,dvm_range=None,dvm_resolution=None):
        # """Measure AC Voltage"""
        # return self.__execute_command("MEAS:","VOLT:AC",dvm_range,dvm_resolution,None,True)

    # def measure_continuity(self):
        # """Measure Contiunity"""
        # return self.__execute_command("MEAS:","CONT",None,True)

    # def measure_diode(self):
        # """Measure Diode"""
        # return self.__execute_command("MEAS:","DIOD",None,True)

    # def measure_dc_current(self,dvm_range=None,dvm_resolution=None):
        # """Measure DC Current"""
        # return self.__execute_command("MEAS:","CURR:DC",dvm_range,dvm_resolution,None,True)
           
    def measure_dc_voltage(self,dvm_range=None,dvm_resolution=None):
        """Measure DC Voltage"""
        return self.__execute_command("MEAS:","VOLT:DC",dvm_range,dvm_resolution,None,True)

    def measure_four_wire_resistance(self,dvm_range=None,dvm_resolution=None):
        """Measure 4 Wire Resistance"""
        return self.__execute_command("MEAS:","FRES",dvm_range,dvm_resolution,None,True)

    def measure_frequency(self,dvm_range=None,dvm_resolution=None):
        """Measure Frequency"""
        return self.__execute_command("MEAS:","FREQ",dvm_range,dvm_resolution,None,True)

    def measure_period(self,dvm_range=None,dvm_resolution=None):
        """Measure Period"""
        return self.__execute_command("MEAS:","PER",dvm_range,dvm_resolution,None,True)

    def measure_ratiometric_dc_voltage(self,dvm_range=None,dvm_resolution=None):
        """Measure ratiometric DC Voltage (high/low)"""
        return self.__execute_command("MEAS:","VOLT:DC:RAT",dvm_range,dvm_resolution,None,True)

    def measure_resistance(self,dvm_range=None,dvm_resolution=None):
        """Measure Resistance"""
        return self.__execute_command("MEAS:","RES",dvm_range,dvm_resolution,None,True)

    #Sample Commands
    def sample_count(self,count=1):
        """Set Sample Count"""
        self.__execute_command("SAMP:","COUN",None,None,count,False)
    
    #Trigger Commands
    
    def trigger_bus(self):
        """Set Trigger Source to BUS"""
        self.__execute_command("TRIG:","SOUR",None,None,"BUS",False)

    def trigger_count(self,count=1):
        """Set Trigger Count"""
        self.__execute_command("TRIG:","COUN",None,None,count,False)

    def trigger_delay(self,delay=0):
        """Set Trigger Delay in Seconds"""
        self.__execute_command("TRIG:","DEL",None,None,delay,False)

    def trigger_external(self):
        """Set Trigger Source to External"""
        self.__execute_command("TRIG:","SOUR",None,None,"EXT",False)

    def trigger_immediate(self):
        """Set Trigger Source  to Immediate"""
        self.__execute_command("TRIG:","SOUR",None,None,"IMM",False)

if __name__=='__main__':
    print "Searching for Agilent 34401A"
    dvm=AGILENT_34401A(debug=False)  
    if dvm.connected:                 
        print "Found "+dvm.identify()+" at address %s" % (dvm.address)
        dvm.reset()                 
    else:
        print "DVM not Found"
    
