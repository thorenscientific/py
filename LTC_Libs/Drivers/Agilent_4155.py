################################################################################
#
# Agilent 4155 Semiconductor Parameter Analyzer Device Driver
#
# Author:Robert Reay
#
# Description:
#   This file contains the driver for the Agilent 4155 using the Flex mode command
#   set. It implements a minimum number of routines to help initiate, read and
#   display measurements. All other commands are implemented directly writing Flex
#   commands. See Agilent_4155_examples.py and the Agilent 4155 programming
#   manual.
#
# Revision History:
#   1-8-2012: Robert Reay
#     Initial code
#
################################################################################

from SCPI_Instrument import *

#data channel keys
Agilent_4155_channels = {'A':'SMU1','B':'SMU2','C':'SMU3','D':'SMU4','E':'SMU5','F':'SMU6','Q':'VSU1','R':'VSU2','S':'VMU1','T':'VMU2','V':'GNDU','W':'PGU1','X':'PGU2'}

class AGILENT_4155(SCPI_Instrument):
    """Agilent 4155 Data Aquisition Driver"""

    def __init__(self,model="4155",address="GPIB0::17",debug=True):
        """Agilent 4156 constructor"""
        SCPI_Instrument.__init__(self,model,address,debug)
        self.__debug=debug
        self.set_timeouts(5000,1000)
    
    def parse_data_string(self,data_string):
        """Split the data string into a list"""
        #A single data_string from the 4155 has the form:
        #AAABCDDDDDDDDDDDDD where A=error code,B=channel,C=type,D=data
        #Example 000AV-1.0000000E-3 (no error,SMU1,Voltage,-1mA)
        #This routine will parse each piece into a list
        if len(data_string)>6:
            status=data_string[0:3]
            channel=data_string[3]
            data_type=data_string[4]
            data=data_string[5:]
            data_list=[status,channel,data_type,data]
        else:
            data_list=[]
        return data_list

    def float_data(self,data_string):
        """Extract the reading from the data string in float format"""
        if len(data_string)>6:
            return float(data_string[5:])
        else:
            return 0

    def __build_data_dictionary(self,data_string):
        """Split the data_string into a dictionary with the channels as keys"""
        data_dict={}
        if len(data_string)>0:
            data_list=data_string.split(',')
            for data in data_list:
                key=Agilent_4155_channels[data[3]]+' ('+data[4]+')'
                if key not in data_dict.keys():
                    data_dict[key] = [data[5:]]
                else:
                    data_dict[key].append(data[5:])
        else:
            if self.__debug: print "Data String Empty"
        return data_dict

    def display_data(self,data_string,print_title=False):
        """Display the returned data in a table"""
        if len(data_string)>0:
            data_dict=self.__build_data_dictionary(data_string)
            output=''
            j=0
            for title in data_dict.keys():
                if j==0:
                    output=output+title.ljust(15)
                else:
                     output=output+'\t'+title.ljust(15)
                j+=1
            if print_title: print output
            data_size=len(data_dict[title])
            for i in range(data_size):
                output=''
                j=0
                for title in data_dict.keys():
                    data_list=data_dict[title]
                    if j==0:
                        output=output+data_list[i].ljust(15)
                    else:
                        output=output+'\t'+data_list[i].ljust(15)
                    j+=1
                print output
        else:
            if self.__debug:print "No Dictionary Data Found"
            
    def initiate_measurement(self):
        """Initiate a measurement"""
        #Override the method from SCPI_Instrument
        self.enable_serial_polling()    #enable serial polling
        self.clear_status()             #clear the status register     
        self.query("*OPC?")             #wait until previous operation is complete
        self.write("XE")                #trigger the measurement
        self.write("*OPC")              #enable operation complete update to the status register
        
    def read_measurement(self,to=1000):
        """Read the meausurement"""
        #for some reason the SRQ signal doesn't seem to work on the debug unit,
        #so the status register (STB) bit 5 is monitored for measurement completion.
        to=to/10
        timeout=True
        for i in range(to):
            x=(int(self.query("*STB?")) & 64)
            if x!=0:
                timeout=False
                break
            self.wait(0.1)
        if not timeout:
            #read the data if no timeout
            data_string=self.query("RMD?")      
            return data_string
        else:
            if self.__debug:print "Read Timeout"
            return ''
          
if __name__=='__main__':
    print "Searching for Agilent 4155"
    vi=AGILENT_4155()   
    if vi.connected:
        print "Found "+vi.identify()+" at address %s" % (vi.address)
    else:
        print '4155 Not Found'
