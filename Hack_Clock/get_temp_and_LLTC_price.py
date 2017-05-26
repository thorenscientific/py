#import pywapi
import ystockquote
import string
import serial
from time import time, strftime, localtime, sleep


def checksum(st):
    return reduce(lambda x,y:x+y, map(ord, st))

def ascsum(sum, numchars):
    return (sum - 48*numchars)


#* you can send the text on the next line using Serial Monitor to set the clock to noon Jan 1 2010 and LLTC to $29.45
#T12623472002945 
#T13246667523036

#rawtime = str(int(time()-28800))
#rawtime = str(int((time()-28800)) - 120 + 0 - 9 + 97 + 3600)
rawtime = str(int((time()-28800)) - 120 + 0 - 9 + 97)

print "Raw Time: " + rawtime

print "Converted Time: " + strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())

rawstock = str(ystockquote.get_price('LLTC'))

print "LLTC Stock Price is " + rawstock

rawstock = ''.join(i for i in rawstock if i.isdigit())
rawstock = rawstock[0:4]

print "Strip the decimal, trim to two " + rawstock

#yahoo_result = pywapi.get_weather_from_yahoo('95035', '')

#print "Yahoo says: It is " + string.lower(yahoo_result['condition']['text']) + " and " + yahoo_result['condition']['temp'] + "F now in Milpitas.\n\n"

#clockstring = "aaaaT" + rawtime + rawstock + "bbbb"
clockstring = "T" + rawtime + rawstock
clockstring = clockstring.encode('utf-8')

# Some test strings without checksums:
#clockstring = "T12623472002945"
#clockstring = "T12623471852945" #  11:59AM shows transition to PM
#clockstring = "T00000300000000" #  checksum less than 10
#clockstring = "T00000345670000" #  checksum less than 100

print "String to send to Clock: " + clockstring
print "Calculate checksum on this: " + clockstring[1:15]
cs = checksum(clockstring[1:15])
print "Normal Checksum: " + str(cs)
rcs = cs - 672 #subtract offset of 14 ASCII "0"
stringrcs = str(rcs)
if len(stringrcs) == 1:
    stringrcs = "00" + stringrcs
elif len(stringrcs) == 2:
    stringrcs = "0" + stringrcs
print "Rich Checksum: " + stringrcs

clockstring = clockstring + stringrcs

#Some test strings with precalculated checksums
#clockstring = "T12623472002945047"
#clockstring = "T12623471852945059" #  11:59AM shows transition to PM

clockser = serial.Serial()
clockser.port = 7
clockser.baudrate = 9600
clockser.parity = serial.PARITY_NONE
clockser.bytesize = serial.EIGHTBITS
clockser.stopbits = serial.STOPBITS_ONE
clockser.timeout = 1.5 #1.5 to give the hardware handshake time to happen
clockser.xonxoff = False
clockser.rtscts = False
clockser.dsrdtr = False
clockser.open()

print clockser

##print "starring delay"
##currenttime = time()
##i=0
##while time() < currenttime + 2:
##    i = i+1
##    #do nothing
##print "end of delay, did it work??"

#numbyteswritten = clockser.write(clockstring)

#Print "wrote " + str(numbyteswritten) + " bytes"

for j in range (0,len(clockstring)):
    clockser.write(clockstring[j])
    print clockstring[j]
    r=0
    for q in range (0,10):
        r = r+1

clockser.close()





