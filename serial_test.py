import serial
import sys
import string


from dc590_rl1009drv import *

DC590ser, RL1009ser = openports()

#test(DC590ser, RL1009ser)

voltage = hp3456a(RL1009ser, 30, 1) #initialize

xchan = 0
ychan = 1
zchan = 2

ltc2704(DC590ser,zchan,0,5.0, 5.0)

print "setting z to 5V"

for y in range(0,13):
    vy = (y * .5) - 3.0
    ltc2704(DC590ser,ychan,0,5.0,vy)
    time.sleep(3.0) #Sleep for a while after reference change
    for x in range(0,25):
        vx = (x * 2* vy / 24) - vy
        ltc2704(DC590ser,xchan,0,5.0,vx)
        time.sleep(0.5)
        voltage = hp3456a(RL1009ser, 30, 0)
        print "vx: " + str(vx) + " vy: " + str(vy) + " output: " + str(voltage)

ltc2704(DC590ser,ychan,0,5.0,3.0)
ltc2704(DC590ser,xchan,0,5.0,1.5)

#ltc2704(DC590ser,0,0,5.0,(1.234))

#print "testing mux board"
#for y in range(0,10):
#    for x in range(0, 15):
#        tppstring = 'U{:02X}2 K02'.format(x)
#        print "tppstring: " + tppstring
#        DC590ser.write(tppstring)
#        #muxboard(DC590ser, x)
#        time.sleep(0.25)


closeports(DC590ser, RL1009ser)
