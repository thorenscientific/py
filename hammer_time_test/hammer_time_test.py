
import string
import serial
import random
from time import time, strftime, localtime, sleep



rawtime = str(int(time()-28800))

print "Basic test of hammer time LED post"


#clockstring = "aaaaT" + rawtime + rawstock + "bbbb"
clockstring = "25"

print "String to send to post: " + clockstring



clockser = serial.Serial()
clockser.port = 19
clockser.baudrate = 115200
clockser.parity = serial.PARITY_NONE
clockser.bytesize = serial.EIGHTBITS
clockser.stopbits = serial.STOPBITS_ONE
clockser.timeout = 1.5 #1.5 to give the hardware handshake time to happen
clockser.xonxoff = False
clockser.rtscts = False
clockser.dsrdtr = False
clockser.open()

print clockser

print "starting delay to let Linduino reset properly..."
sleep(5)

numbyteswritten = clockser.write(clockstring)

print "wrote " + str(numbyteswritten) + " bytes"

# Command set:
# t12 - set top window, 12 is example argument, 2 hex characters, 130 maximum
# b34 - set bottom window, 34 is example argument
# pAB - set ball position, AB is example argument

for i in range(100):
    clockser.write(str(i))
    sleep(1)
    top = random.randint(70, 119)
    bottom = random.randint(0, 50)
    ball = random.randint(bottom+1, top-1)

    command = "t{:02X}".format(top)
    print("command: " + command)
    clockser.write(command)
    sleep(0.1)
    
    command = "b{:02X}".format(bottom)
    print("command: " + command)
    clockser.write(command)
    sleep(0.1)
    command = "p{:02X}".format(ball)
    print("command: " + command)
    clockser.write(command)    
#    updown = 1
#    for j in range (5):
    



clockser.close()





