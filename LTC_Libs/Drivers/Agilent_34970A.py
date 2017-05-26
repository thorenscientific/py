################################################################################
#
# Agilent 34970A Data Aquisition Switch Unit Device Driver
#
# Author:Robert Reay
#
# Description:
#   This file is a driver for the Agilent 34970A based on the SCPI Instrument class.
#   Not all commands are implemented.
#
# Revision History:
#   1-5-2013: Robert Reay
#     Modify to use the SCPI_Instrument class.
#     Added input impedance commands
#   9-25-2012: Robert Reay
#     Initial code
#
################################################################################

from SCPI_Instrument import *

class AGILENT_34970A(SCPI_Instrument):
    """Agilent 34970A Data Aquisition Driver"""
      
    def __init__(self,model="34970A",address="GPIB0::9",debug=False):
        """Agilent 34970A constructor"""
        SCPI_Instrument.__init__(self,model,address,debug)

    def __execute_command(self,prefix="MEAS:",function="VOLT:DC",channel_list=[101],dvm_range=None,dvm_resolution=None,dvm_value=None,use_query=True):
        """Execute the dvm command"""
        if type(channel_list).__name__=='int':                  #convert to list if necessary
            channel_list=[channel_list]
        channel_count=len(channel_list)                         #get the channel count
        command=str(prefix)+str(function)                       #contatinate the prefix and function
        if use_query:                                           #if command requires a query, add '?'
            command+="?"
        if ((dvm_range!=None) & (dvm_resolution!=None)):        #check for range and resolution specified
            command+=" "+str(dvm_range)+","+str(dvm_resolution) #add to command string if specified
            if channel_count!=0:
                command+=","                                    #if the channels are specified, add a ','
        if dvm_value!=None:                                     
            command+=" "+str(dvm_value)+","
        if channel_count!=0:                                    
            command+=" (@"                                      #build the channel list
            for i in range(len(channel_list)):
                command+=str(channel_list[i])
                if i!=channel_count-1:
                    command+=","
            command+=")"
        if use_query:
            if channel_count>1: 
                return self.query(command).split(",")           #return an array of voltages if more than 1 channel
            else:
                return self.query(command)                      #return 1 voltage if 1 channel
        else:
            self.write(command)

    def abort_scan(self):
        """abort the scan"""
        self.write("ABORT")
      
    def close_switch(self,channel_list=[101]):
        """close a switch"""
        return self.__execute_command("ROUT:","CLOSE",channel_list,None,None,None,False)

    def four_wire_off(self,channel_list=[101]):
        """turn 4-wire measurement off"""
        return self.__execute_command("ROUT:","CHAN:FWIRE",channel_list,None,None,"OFF",False)

    def four_wire_on(self,channel_list=[101]):
        """turn 4-wire measurement on"""
        return self.__execute_command("ROUT:","CHAN:FWIRE",channel_list,None,None,"ON",False)

    def configure_ac_current(self,channel_list=[121],dvm_range=None,dvm_resolution=None,nplc=None):
        """Configure ac current."""
        self.__execute_command("CONF:","CURR:AC",channel_list,dvm_range,dvm_resolution,None,False)
        if nplc!=None:
            self.__execute_command("SENS:","CURR:AC:NPLC",channel_list,None,None,nplc,False)

    def configure_ac_voltage(self,channel_list=[101],dvm_range=None,dvm_resolution=None,nplc=None):
        """Configure ac volts."""
        self.__execute_command("CONF:","VOLT:AC",channel_list,dvm_range,dvm_resolution,None,False)
        if nplc!=None:
            self.__execute_command("SENS:","VOLT:AC:NPLC",channel_list,None,None,nplc,False)

    def configure_dc_current(self,channel_list=[121],dvm_range=None,dvm_resolution=None,nplc=None):
        """Configure dc current."""
        self.__execute_command("CONF:","CURR:DC",channel_list,dvm_range,dvm_resolution,None,False)
        if nplc!=None:
            self.__execute_command("SENS:","CURR:DC:NPLC",channel_list,None,None,nplc,False)
    
    def configure_dc_voltage(self,channel_list=[101],dvm_range=None,dvm_resolution=None,nplc=None):
        """Configure dc volts."""
        self.__execute_command("CONF:","VOLT:DC",channel_list,dvm_range,dvm_resolution,None,False)
        if nplc!=None:
            self.__execute_command("SENS:","VOLT:DC:NPLC",channel_list,None,None,nplc,False)

    def configure_digital_input(self,channel_list=[301]):
        """Configure digital input."""
        self.__execute_command("CONF:","DIG:BYTE",channel_list,None,None,None,False)

    def configure_four_wire_resistance(self,channel_list=[101],dvm_range=None,dvm_resolution=None,nplc=None):
        """Configure dc volts."""
        self.__execute_command("CONF:","FRES",channel_list,dvm_range,dvm_resolution,None,False)
        if nplc!=None:
            self.__execute_command("SENS:","FRES:NPLC",channel_list,None,None,nplc,False)

    def configure_frequency(self,channel_list=[101],dvm_range=None,dvm_resolution=None,aperature=None):
        """Configure frequency."""
        self.__execute_command("CONF:","FREQ",channel_list,dvm_range,dvm_resolution,None,False)
        if aperature!=None:
            self.__execute_command("SENS:","FREQ:APER",channel_list,None,None,aperature,False)

    def configure_period(self,channel_list=[101],dvm_range=None,dvm_resolution=None,aperature=None):
        """Configure frequency."""
        self.__execute_command("CONF:","PER",channel_list,dvm_range,dvm_resolution,None,False)
        if aperature!=None:
            self.__execute_command("SENS:","PER:APER",channel_list,None,None,aperature,False)

    def configure_resistance(self,channel_list=[101],dvm_range=None,dvm_resolution=None,nplc=None):
        """Configure dc volts."""
        self.__execute_command("CONF:","RES",channel_list,dvm_range,dvm_resolution,None,False)
        if nplc!=None:
            self.__execute_command("SENS:","RES:NPLC",channel_list,None,None,nplc,False)

    def configure_temperature(self,channel_list=[101],transducer="TC",transducer_type="J",nplc=None):
        """Configure temperature."""
        #Transducer Values : TC,RTD,FRTD,THERM
        #Transducer Types  : TC=B,E,J,K,N,R,S,T
        #See manual for more detail
        self.__execute_command("CONF:","TEMP",channel_list,None,None,transducer+","+transducer_type,False)
        if nplc!=None:
            self.__execute_command("SENS:","TEMP:NPLC",channel_list,None,None,nplc,False)

    def dac_output(self,channel_list=[304],voltage=0):
        """Write DAC voltage."""
        #DAC1 on channel 4, DAC2 on channel 5
        self.__execute_command("SOUR:","VOLT",channel_list,None,None,voltage,False)

    def digital_output(self,channel_list=[302],data=0):
        """Write digital output byte."""
        #lsb on channel 1, msb on channel 2
        self.__execute_command("SOUR:","DIG:DATA:BYTE",channel_list,None,None,data,False)
   
    def measure_ac_current(self,channel_list=[121],dvm_range=None,dvm_resolution=None):
        """Measure ac current."""
        return self.__execute_command("MEAS:","CURR:AC",channel_list,dvm_range,dvm_resolution,None,True)
    
    def measure_ac_voltage(self,channel_list=[101],dvm_range=None,dvm_resolution=None):
        """Measure ac volts."""
        return self.__execute_command("MEAS:","VOLT:AC",channel_list,dvm_range,dvm_resolution,None,True)

    def measure_dc_current(self,channel_list=[121],dvm_range=None,dvm_resolution=None):
        """Measure dc current."""
        return self.__execute_command("MEAS:","CURR:DC",channel_list,dvm_range,dvm_resolution,None,True)
    
    def measure_dc_voltage(self,channel_list=[101],dvm_range=None,dvm_resolution=None):
        """Measure dc volts."""
        return self.__execute_command("MEAS:","VOLT:DC",channel_list,dvm_range,dvm_resolution,None,True)

    def measure_digital(self,channel_list=[301]):
        """Measure digital byte"""
        return self.__execute_command("MEAS:","DIG:BYTE",channel_list,None,None,None,True)

    def measure_four_wire_resistance(self,channel_list=[101],dvm_range=None,dvm_resolution=None):
        """Measure dc volts."""
        return self.__execute_command("MEAS:","FRES",channel_list,dvm_range,dvm_resolution,None,True)

    def measure_frequency(self,channel_list=[101],dvm_range=None,dvm_resolution=None):
        """Measure frequency."""
        return self.__execute_command("MEAS:","FREQ",channel_list,dvm_range,dvm_resolution,None,True)

    def measure_period(self,channel_list=[101],dvm_range=None,dvm_resolution=None):
        """Measure frequency."""
        return self.__execute_command("MEAS:","PER",channel_list,dvm_range,dvm_resolution,None,True)

    def measure_resistance(self,channel_list=[101],dvm_range=None,dvm_resolution=None):
        """Measure dc volts."""
        return self.__execute_command("MEAS:","RES",channel_list,dvm_range,dvm_resolution,None,True)

    def measure_temperature(self,channel_list=[101],transducer="TC",transducer_type="J"):
        """Measure temperature."""
        #Transducer Values : TC,RTD,FRTD,THERM
        #Transducer Types  : TC=B,E,J,K,N,R,S,T
        #See manual for more detail
        return self.__execute_command("MEAS:","TEMP",channel_list,None,None,transducer+","+transducer_type,True)
       
    def monitor_channel(self,channel=101):
        """Monitor Channel."""
        value="(@"+str(channel)+")"
        self.__execute_command("ROUT:","MON",[],None,None,value,False)

    def monitor_off(self):
        """Turn Monitor Off"""
        self.__execute_command("ROUT:","MON:STAT",[],None,None,"OFF",False)
        
    def monitor_on(self):
        """Turn Monitor On"""
        self.__execute_command("ROUT:","MON:STAT",[],None,None,"ON",False)

    def impedance_high(self):
        """High input impedance"""
        self.write("INPUT:IMPEDANCE:AUTO ON")

    def impedance_low(self):
        """Low input impedance"""
        self.write("INPUT:IMPEDANCE:AUTO OFF")

    def open_switch(self,channel_list=[121]):
        """open a switch"""
        self.__execute_command("ROUT:","OPEN",channel_list,None,None,None,False)

    def scan(self,channel_list=[121]):
        """define the scan list"""
        self.__execute_command("ROUT:","SCAN",channel_list,None,None,None,False)

    def trigger_bus(self):
        """set bus trigger"""
        self.__execute_command("TRIG:","SOUR",[],None,None,"BUS",False)

    def trigger_count(self,count=1):
        """set trigger count"""
        self.__execute_command("TRIG:","COUNT",[],None,None,count,False)
    
    def trigger_immediate(self):
        """set immediate trigger"""
        self.__execute_command("TRIG:","SOUR",[],None,None,"IMM",False)

    def trigger_timer(self):
        """set timer trigger"""
        self.__execute_command("TRIG:","SOUR",[],None,None,"TIM",False)

if __name__=='__main__':
    print "Searching for Agilent 34970A"
    dvm=AGILENT_34970A(debug=True)
    if dvm.connected:
        print "Found "+dvm.identify()+" at address %s" % (dvm.address)
