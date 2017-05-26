#-------------------------------------------------------------------------------
# Name:        ProcessCmd.py
# Purpose:     This module reads data from a file and converts the data to 
#              foramt suitable to be directly sent to the tower module.
#
#              Based on the 'X' command, this module makes conversion to the
#              values in the file passed to it. It mainly converts the analog
#              volatge to appropriate digital hex values
#
# Author:      Navin
#
# Created:     15/07/2011
# Copyright:   (c)MDN
# Licence:     MDN licence
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from TwrLtc import TwrLtc

CHIPS = ["ltc2600",          #X0 
         "ltc2704",          #X1
         "ltc2498",          #x2
         "ltc1859"           #x3 
         ]

class IvalidInputError(Exception):
	pass

class ProcessCmd:
	""" This class implements methods required to process the data present in 
	the input command file """
	
	def __init__(self, inp_cmd = 'cmds.txt'):
		""" This constructor tries to open the input command file. If the file 
		could not be opened then a exception is raised """
		try:
			self.inp_file = open(inp_cmd, 'r')
		except IOError:
			raise IOError, "Could not open the file %s " %inp_cmd
			
		self.twr_pro = TwrLtc()       # Variable to access ltc chip methods
			
	def process(self, out_cmd = 'cmds_pro.txt'):
		""" The input commands file is read and processed and stored in the file
		with name as specified in out_file. The default output file name is 
		cmds_pro.txt. If for some reasons, the file could not be opened then
		IOError exception is raised  """
		try:
			self.out_file = open(out_cmd, 'w')
		except IOError:
			raise IOError, "Could not open the file %s " %out_cmd
			
		# get the commands from the file
		cmds = self.inp_file.readlines()
		
		current_chip = ""
		line_num = 0
		for cmd in cmds:
			if cmd[0] == 'X':
				# A chip select
				try:
					chip_ind = int(cmd[1]) # try and make sense out of the X cmd
				except ValueError:
					raise InvalidInputError, "process(): Invalid input in the \
					                   file at line number %d " %(line_num+1)
				if chip_ind >= len(CHIPS):
					# trying to select invalid chip
					raise InvalidInputError, "process(): Invalid input in the \
					                   file at line number %d " %(line_num+1)
				current_chip = CHIPS[chip_ind]
				
			elif cmd[0] == 'S':
				cur_line = cmd.replace('S', '')
				try:
					val = float(cur_line)
				except ValueError:
					raise InvalidInputError, "process(): Expected a number at \
					%d" %(line_num)
				if current_chip == "ltc2600":
					hex_val = self.twr_pro.ltc2600_data(cur_line)  # get the hex rep
					op_cmd = 'S'+hex_val                 # form the cmd
				elif current_chip == "ltc2704":
					hex_val = self.twr_pro.ltc2704_data(cur_line)
					op_cmd = 'S'+hex_val
				else:
					op_cmd = 'S'+ '0000'
				
					
				self.out_file.write(op_cmd+ '\n')
				continue
				
			self.out_file.write(cmd)
			line_num += 1
			


def test():
	
	try:
		test_obj = ProcessCmd('test_cmds.txt')				 
	except IOError, msg:
		print "Error in opening file "
		print msg
		return
		
	try:
		test_obj.process()
	except IOError, msg:
		print msg
	except IvalidInputError, msg:
		print msg
		

if __name__ == '__main__':
	test()
	
 
		
