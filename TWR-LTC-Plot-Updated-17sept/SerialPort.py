#-------------------------------------------------------------------------------
# Name:        SerialPort.py
# Purpose:     Module for commnicating with the DMM and the tower over serial
#              port.
#
# Author:      Navin
#
# Created:     14/07/2011
# Copyright:   (c)MDN
# Licence:     MDN licence
#-------------------------------------------------------------------------------
#!/usr/bin/env python


import serial,sys
import time, re, string
""" This file implements functions required for commmunication with Arduino
over the serial port """

class SerialPort:
	""" This class initializes the serial port at 9600 baudrate. optinally,
	pass the comport number other wise, com 1 is taken as default """	
	
	def __init__(self, port = 'COM1', baudrate = '115200', stopbits = '1'):
		"""Constructor for serial port"""
		if type(port) != type(""):
			raise TypeError, "I was expecting string but received %s" %type(port)
		try:
			self.serialPort = serial.Serial(port)
		except serial.SerialException:
			raise IOError, "Could not open serial port: %s " %port 
		bytesize = '8'
		parity = 'N'
		self.serialPort.baudrate = int(baudrate)
		self.serialPort.bytesize = int(bytesize)
		self.serialPort.parity   = parity
		self.serialPort.stopbits = int(stopbits)
		self.serialPort.timeout  = 2
		self.serialPort.XonXoff  = None
		return


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# this is used to close the serial port

	def close_port(self):
		""" This method closes the serial port """
		self.serialPort.close()
		return

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# this is used to write to the port

	def write_to_port(self,command):
		""" This method reads what the Arduino has to say """
		command.strip("\n")
		self.serialPort.flushOutput()
		self.serialPort.writelines(command)
		self.serialPort.flushInput()        # we don't want to read echoed charcters
		self.serialPort.write("\r")
		time.sleep(0.01)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	
		
		
# this is used to read from the port

	def read_from_twr(self):
		portBuffer = ""
		returnval = False
		for i in range(0,700):
			           
			time.sleep(0.01)
			while (self.serialPort.inWaiting() > 0):
				temp = self.serialPort.read()
				portBuffer += temp

			if (re.search("OK",portBuffer)):
				returnval = True
				break
				
			
			
		res = portBuffer.strip("OK").replace("\r\n", '')
		res = res.replace('OK', '')
			
		return (res, returnval)
        
	def read_from_dmm(self):
		portBuffer = ""
		returnval = False
		once = False         # we read twice to avoid polluted readings 
		# since the readings comming from the DMM are not in sync
		self.serialPort.flushInput()
		
		for i in range(0,700):  
			time.sleep(0.01)
			while (self.serialPort.inWaiting() > 0):
				temp = self.serialPort.read()
				if temp == '+' or temp == '-':
					if once == False:
						portBuffer = temp
						once = True
						continue
						
				if once == True and temp == '\r':
					returnval = True
					break
					
				else:
					portBuffer += temp
				
					
			if returnval == True:
				break
				 	
		res = portBuffer.replace("\r\n", '')
		res = res.replace('\r\n', '')
		self.serialPort.flushOutput()
		
		try:
			val = float(res)
		except ValueError:
			val = 0.0
			returnval = False
			
		return (val, returnval)
				
        

if __name__ == '__main__':
	try:
		ser = SerialPort('COM6', baudrate='9600', stopbits = 2)
		for i in range(10):
			ret = ser.read_from_dmm()
			
			if ret[1] == True:
				#val = float(ret[0])
				print "Volatge is %f " %ret[0]
				#time.sleep(1000)
			else:
				print "There was an error "
	except IOError:
		pass


