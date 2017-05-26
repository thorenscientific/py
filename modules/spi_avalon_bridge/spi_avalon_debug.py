# Import libraries
from memory_tester_util import *
import time

try:
    dc590 = DC590() ## Look for the DC590
    dc590.transfer_packets('G', 0) # Set the GPIO HIGH 
    

    data_packet = transaction_read(dc590,640, 64)
    print x       
    print data_packet
    print "****************************"

#    for x in range(0,3):
#        data_packet = transaction_read(dc590,536869888+(1024*x), 1024)
#        print x       
#        print data_packet
#        print "****************************"
#    
    
    dc590.transfer_packets('g', 0) # Set the GPIO LOW
finally:
    dc590.close()
print 'Done!'    