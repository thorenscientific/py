#-------------------------------------------------------------------------------
# Name:        CSVLog.py
# Purpose:     This module writes volatge data to a CSV file
#
# Author:      Navin
#
# Created:     18/07/2011
# Copyright:   (c)MDN
# Licence:     MDN licence
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import csv


class CSVLog:
	""" This class provides methods to log data in CSV format """
	
	def __init__(self, file_name):
		""" Prepares the file for logging data.Raises ValueError exception is
		file_name is not string. Raises IOError if file could not be opened.
		"""
		
		if type(file_name) != type(""):
			raise ValueError, "CSVLog() requires file_name to be of string type"
			
		try:
			self.log_file = open(file_name, 'wt')
		except IOError:
			raise IOError, "Could not open file %s " %file_name
		
		self.log_writer = csv.writer(self.log_file)
		
	def write_title(self, title):
		""" This methods adds a title to the csv log file. The argument title 
		must be of type list """
		
		if type(title) != type([]):
			raise ValueError, "write_title() requires a string "
			
		self.log_data(title)
		
	def log_data(self, data):
		""" This method logs the data into the csv file. Raises exception if
		data is not a list """
		
		if type(data) != type([]):
			raise ValueError, "write_data() requires a list type "
			
		self.log_writer.writerow(data)
		

		
		
