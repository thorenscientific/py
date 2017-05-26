################################################################################
#
# Macros
#
# Author:Robert Reay
#
# Description:
#   This program contains subroutines to help make programming easier
#
# Revision History:
#   9-11-2012: Robert Reay
#       Initial code
#   12-28-2012: Robert Reay
#       Add the engineering format routine
#
################################################################################

from math import *

def get_integer(prompt="Enter Value: ",min_value=0,max_value=0):
    """Read an integer"""
    #get a base8, base10 or base16 number from the user
    data=raw_input(prompt)
    try:
        if data.find("0x")==0:    #Check for HEX
            value=int(data,16)
        elif data.find("0X")==0:  #Check for HEX
            value=int(data,16) 
        elif data.find("O")==0:   #Check for OCTAL
            value=int(data,8)
        elif data.find("o")==0:   #Check for OCTAL
            value=int(data,8) 
        else:
            value=int(data)
    except:
        value=0
        if value<min_value: value=min_value    #Check min value
        if value>max_value: value=max_value    #Check max value
    return value

def engineering_format(value,units='',digits=4,min_value=None,max_value=None,separator=''):
    """Transform a value to engineering format"""
    #units: units character
    #digits: the total number of digits before and after the decimal place
    #min_value: Any value or digits lower than min_value will be formated as zero
    #max_value: Any value higher than max_value will be formatted at max_value
    #separator: Character between value and units
    d=['y','z','a','f','p','n','u','m','','k','M','G','T','P','E','Z','Y']
    if min_value!=None:        
        if abs(value)<min_value:
            s='0.'
            for i in range(1,digits):
                s=s+'0'
            return s+" "+str(units)
        if abs(min_value)>=1:
            pm=-1*int(log10(abs(min_value+1e-10)))
        else:
            pm=-1*(int(log10(abs(min_value-1e-10)))-1)
            value=round(value,pm)
    if max_value!=None:
        if abs(value)>max_value:
            value=max_value
    if value==0:
        fs="%1."+str(digits-1)+"f"+separator+str(units)
        return (fs % 0)
    if abs(value)>=1:
        p=int(log10(abs(value+1e-10)))
    else:
        p=int(log10(abs(value-1e-10)))-1
    rng=int(p/3)
    rem=int(p%3)
    dp=digits-rem-1
    f=rem+dp*(0.1)
    fs="%"+str(f)+"f"+separator+d[rng+8]
    if (units!=None):
        fs+=str(units)
    m=pow(1000,rng)
    return(fs % (value/m))

if __name__=='__main__':
    x=get_integer(prompt="Enter Integer: ",min_value=0,max_value=100)
    print "You Entered: %d" % x
    y=engineering_format(x,'V',5,0,100,'')
    print "Formatted Value: %s" % y  
