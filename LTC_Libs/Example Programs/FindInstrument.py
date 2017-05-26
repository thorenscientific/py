################################################################################
#
# Instrument Scan 
#
# Author:Robert Reay
#
# Description:
#   Scan the GPIB address space for connected instruments using the RL1009 USB
# to GPIB controller.
#
# Revision History:
#   11-20-2011: Robert Reay
#   Initial code
#
################################################################################

from RL1009_DLL_INTERFACE import *
    
def find_instrument(modelName='34401A'):
    print "Search for %s ..." % modelName
    r=RL1009()
    r.set_timeouts(100,100)
    r.set_terminator(1)
    for i in range(32):
        id=r.query("*IDN?",i)
        splitId=id.split(',')
        print i,id
        #for an instrument there are 4 fields,
        # 0: manufacturer, 1: model, 2:?, 3:version
        if (len(splitId)>2):
            idName=id.split(',')[1]
            if (idName==modelName):
                print "Instrument %s found at address %i." % (modelName,i)
                return i
    print "No %s found." % modelName
    return -1
  

if __name__=='__main__':
    a=find_instrument('34401A')
    b=find_instrument('34401B') #does it return -1?
    c=find_instrument('FSU-8')
    d=find_instrument('E3631A')
    print a,b,c,d
