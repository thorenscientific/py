################################################################################
#
# Instrument Scan 
#
# Author:Robert Reay
#
# Description:
#   Scan the GPIB address space for connected instruments using the RL1009 USB
# to GPIB controller or VISA controller
#
# Revision History:
#   1-5-2013: Robert Reay
#     Added the VISA connection
#   11-20-2011: Robert Reay
#     Initial code
#
################################################################################

from RL1009_DLL_INTERFACE import *
from visa import *

def get_instrument_list():
    print "Starting Instrument Search ..."
    #Search the RL1009
    r=RL1009()
    if r.connected():
        r.set_timeouts(100,100)
        r.set_terminator(1)
        for address in range(32):
            id_string=r.query("*IDN?",address)
            print "RL1009::%d\t %s" % (address,id_string) 
    #Search VISA
    try:
        instrument_list=get_instruments_list(True)
    except:
        pass
    else:
        for i in range(len(instrument_list)):
            try:
                visa=instrument(instrument_list[i])
            except:
                pass
            else:
                id_string=visa.ask("*IDN?")
                print "%s\t %s" % (instrument_list[i],id_string)        
    print "Search Complete"
    
if __name__=='__main__':
    get_instrument_list()

    
