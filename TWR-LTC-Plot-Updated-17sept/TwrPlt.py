#-------------------------------------------------------------------------------
# Name:        TwrPlot.py
# Purpose:     This application plots the analog volatges read by the TWR-LTC
#              and by HP34401A multi meter. 
#
# Author:      Navin Bhaskar
#
# Created:     14/07/2011
# Copyright:   (c)MDN
# Licence:     MDN licence
# Reference:   http://eli.thegreenplace.net/2008/08/01/matplotlib-with-wxpython-guis/
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import pprint
import random
import sys
import wx

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
from threading import Thread
from SerialPort import SerialPort
import time
from TwrLtc import TwrLtc
from ProcessCmd import ProcessCmd


MAX_WIDTH = 50


class DatAcqThread(Thread):
	""" This is the subclassing of the Thread class and is responsible for 
	acquiring data from the tower and multimiter and logs the data for plotting
	them """	
	def __init__(self, mainFrame):
		""" This is the constructor for this thread. This one initializes the 
		thread  """
		Thread.__init__(self)
		self.controller = mainFrame
		self.setDaemon(True)
		self.sample_number = 0
		self.dac_cmd = ""        # Holds the command sent to DAC
		
	def get_smaple_number(self):
		""" This getter method returns the current value of sample_number """
		return (self.sample_number)
		
	def set_sample_number(self, new_val):
		""" This methods sets  sample_number to a new value. Raises exception
		if new_val is not of type int  """
		if type(new_val) != type(1):
			raise ValueError , "set_sample_number() requires an integer arg "
			
		if new_val < 0:
			self.sample_number = 0
		else:
			self.sample_number = new_val
			
	def __inc_sample_number__(self):
		""" This mehod incerments the sample_number by 1 and returns the 
		incremented value """
		self.sample_number += 1
		return (self.sample_number)
		
		
	def run(self):
		""" This is the "action" part of the thread. This simply reads the 
		data from the Tower and the multimiter.
		NOTE: The serial ports for comminucation must opened by the main frame 
		""" 
		twrpro = TwrLtc()   # for Data conversion/interpretation 
		self.set_sample_number(0) # clear the number of samples 

		while 1:
			op_file = open(self.controller.cmds_file, 'r') # open the commands file
			lines = op_file.readlines()
			for line in lines:
				try:
					
					self.controller.twr_data_acq.write_to_port(line)
					
					if line.find('R') >= 0:
						# Reading from ports required
						# Read from the tower
						time.sleep(0.5) # allow ADC, DMM to settle
						
						twr_vltg = self.controller.twr_data_acq.read_from_twr()
						if twr_vltg[1] == True:
							# Valid data acquired 
							if self.chip_mux == '2':
								twr_val = twrpro.ltc2498_data(twr_vltg[0])
							elif self.chip_mux == '3':
								twr_val = twrpro.ltc1859_data(twr_vltg[0])
						else:
							twr_val = 0
						# While the DAC is outputing the voltage read by TWR's
						# ADC, Let us measure the volatge measured by DMM
						
						dmm_vltg = self.controller.dmm_data_acq.read_from_dmm()
						if dmm_vltg[1] == True:
							dmm_val = float(dmm_vltg[0])
						else:
							dmm_val = 0
								
						samp = self.__inc_sample_number__()	 # increment the sample number
						wx.CallAfter(self.controller.log_plot, [samp, self.dac_cmd, dmm_val, twr_val ])
						
					elif line.find('X') >= 0:
						# A chip selection is being performed
						self.chip_mux = line[1]   # the chuip mux
						if line[1] == '0':   # the ltc2600 DAC has been selected
							# get the command sent to the DAC
							sleep_delay = 0.01
							self.dac_cmd = line
						elif line[1] == '1': 
							# the ltc2704 DAC was selected
							self.dac_cmd = line
							time.sleep(1)
							sleep_delay = 5
							continue
						elif line[1] == '3':
							time.sleep(1)
							sleep_delay = 5
							continue
						
							
					op_file.close()	
					time.sleep(sleep_delay) # wait for some time befrore starting the 
									 # next cycle 

				except AttributeError:
					# The main thread has ended ?
					return 
					
			try:
				if self.controller.cbLoop.GetValue() == False:
					break
			except AttributeError:
				return 
			
			

class GraphFrame(wx.Frame):
	""" This is the frame on which we will have the graph and other controls 
	This will hold the panel on which we will be displaying the Graph """
	
	def __init__(self, title):
		""" The constructor which constructs the GUI and initializes
		this application """
		
		wx.Frame.__init__(self, None, -1, title, size=(750, 650))
		self.twr_data = [3]         # start with a dummy value for data acquired
									# from the tower
		self.dmm_data = [3]         # start data for DMM readings
		self.create_panel() 			# construct the panel
		
		
	def init_plot(self):
		""" This method creates the graphs and adds two sub plots to the main 
		graph. This method alos initializes the graphs """
		self.dpi = 100
		self.fig = Figure((3.0, 3.0), dpi=self.dpi)
		self.twr_graph = self.fig.add_subplot(111)   # tower graph
		self.winWidthMax = MAX_WIDTH
		self.winWidthMin = self.winWidthMax - MAX_WIDTH
		
		
		# set title for the Graph
		self.twr_graph.set_title('TWRLTC plot demo')
		# set fonts for the tick labels (the numbers that appear below the x 
		# axes and right before the y axes )
		pylab.setp(self.twr_graph.get_xticklabels(), fontsize=8)
		pylab.setp(self.twr_graph.get_yticklabels(), fontsize=8)
		
		# set color attributes for the TWR and DMM plots. Set the grid color 
		self.twr_plot_data = self.twr_graph.plot(self.twr_data, linewidth=1,color='r',)[0]
		self.dmm_plot_data = self.twr_graph.plot(self.dmm_data, linewidth=1,color='m',)[0]
		self.twr_graph.grid(True, color='black') 
		
		# set the legend
		self.twr_graph.legend([self.twr_plot_data, self.dmm_plot_data], ["TWR LTC", "DMM"], loc=1)
		
	 
	
	def create_panel(self):
		""" This method creates the main pannel and creates other GUI components
		"""
		thePan = wx.Panel(self)    # The main pannel on which we will have
										# the graph and the other GUI controls
		sidPan = wx.Panel(thePan, size=(30, 50))
		# sidPan (side pannel) holds only the GUI controls
		
		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(10)
		self.init_plot()
		self.canvas = FigCanvas(thePan, -1, self.fig)
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW) 
		vbox.AddSpacer(10)
		vbox.Add(sidPan, 0, flag=wx.BOTTOM | wx.GROW)
		
		spvbox = wx.BoxSizer(wx.VERTICAL)
		
		
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.cbLoop = wx.CheckBox(sidPan, -1, "Loop over input commands file")
		hbox1.Add(self.cbLoop, flag = wx.LEFT | wx.CENTER, border = 10)
		self.start_btn = wx.Button(sidPan, label='Start', size=(70,30))
		hbox1.Add(self.start_btn)
		self.pause_btn = wx.Button(sidPan, label='Pause', size=(70, 30) )
		self.save_btn = wx.Button(sidPan, label='Save', size=(70, 30) )
		hbox1.Add(self.pause_btn, flag=wx.LEFT | wx.BOTTOM, border=5)
		hbox1.Add(self.save_btn, flag=wx.LEFT | wx.BOTTOM, border=5)
		self.pause_btn.Bind(wx.EVT_BUTTON, self.on_pause)
		self.start_btn.Bind(wx.EVT_BUTTON, self.on_start)
		self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		self.save_btn.Disable()
		
		spvbox.Add(hbox1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)
		
	
		sidPan.SetSizer(spvbox)
		thePan.SetSizer(vbox)
		
		
		
		self.paused = False       # To indicate if the plotting has to be paused
		
	def plot_data(self):
		""" This function plots the data on the graph """
		twr_xmax = len(self.twr_data) if len(self.twr_data) > MAX_WIDTH else MAX_WIDTH
		twr_xmin = twr_xmax - 50
		
		twr_ymin = round(min(self.twr_data), 0) - 1
		twr_ymax = round(max(self.twr_data), 0) + 1
		
		
		dmm_xmax = len(self.dmm_data) if len(self.dmm_data) > MAX_WIDTH else MAX_WIDTH
		dmm_xmin = dmm_xmax - 50
		
		dmm_ymin = round(min(self.dmm_data), 0) - 1
		dmm_ymax = round(max(self.dmm_data), 0) + 1
		
		
		self.twr_graph.set_xbound(lower=dmm_xmin, upper=dmm_xmax)
		self.twr_graph.set_ybound(lower=dmm_ymin, upper=dmm_ymax)
		
		
		pylab.setp(self.twr_graph.get_xticklabels(), visible=True)
		
		self.twr_plot_data.set_xdata(np.arange(len(self.twr_data)))
		self.twr_plot_data.set_ydata(np.array(self.twr_data))
		
		self.twr_graph.hold(True)
		self.twr_graph.plot(self.dmm_data, linewidth=1,color='m',)
		self.twr_graph.set_xbound(lower=dmm_xmin, upper=dmm_xmax)
		self.twr_graph.set_ybound(lower=dmm_ymin, upper=dmm_ymax)
		self.canvas.draw()
		
	def on_pause(self, event):
		if self.paused == True:
			self.paused = False
			self.pause_btn.SetLabel('Pause')
		else :
			self.paused = True
			self.pause_btn.SetLabel('Resume')
		
	def on_start(self, event):
		from TwrLtcConfig import ConfigFrame
		from CSVLog import CSVLog
		configs = self.TwrLtcConfig()
		
		frame = ConfigFrame(self, configs)
		frame.ShowModal()
		
		if configs.get_valid_configs() == True:
			# User inputs have passed the basic test Let us proceed with 
			# those values 
			# No more error checkings on serial ports are required here
			# Let us not have any error checking here
			try:
				self.twr_data_acq = SerialPort(configs.get_twr_ser_port())
			except IOError:
				wx.MessageBox("Could not open serial port %s for communicating with the tower " %configs.get_twr_ser_port())
				return 
				
			try:
				self.dmm_data_acq = SerialPort(configs.get_dmm_ser_port(), '9600', stopbits='2')
			except IOError:
				wx.MessageBox("Could not open serial port %s for communicating with the HP34001A " %configs.get_dmm_ser_port())
				self.twr_data.acq.close_port()
				return 
				
				
			
			self.logger = CSVLog(configs.get_log_file())
			pro = ProcessCmd(configs.get_cmd_file())  # The commands will be processed and
			self.cmds_file = 'cmds_pro.twrcmd'
			pro.process(self.cmds_file)            # stored in 'cmds_pro.txt' pass
			# differnt file name to process() to change this behaviour
			del pro
			
			self.logger.write_title(['Sample number', 'Command sent to DAC', \
			'Voltages read by DMM', 'Volatges read by TWRLTC'])
			self.save_btn.Enable()
			self.start_btn.Disable()
			acq_thread = DatAcqThread(self)
			acq_thread.start()
			
	def on_save(self, event):
		file_choices = "PNG (*.png)|*.png"
		dlg = wx.FileDialog(self, message="Save plot as...",defaultDir=os.getcwd(),defaultFile="plot.png",
		wildcard=file_choices,style=wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.canvas.print_figure(path, dpi=self.dpi)
	    
				
	
	def log_plot(self, dat):
		
		if self.paused == False:
			self.twr_data.append(dat[3])
			self.dmm_data.append(dat[2])
			self.logger.log_data(dat)
			self.plot_data()
		else:
			# Ignore the data, drop them
			pass 
						
	def __del__(self):
		try:
			plotThread.stop()
		except AttributeError:
			pass
		
		
	class TwrLtcConfig:
		""" A class that groups all the configuration information for TwrLtc 
		plot demo """
		
		def __init__(self):
			""" Initializes the required data members """
			self.twr_ser_port = ""
			self.dmm_ser_port = ""
			self.cmd_file = ""
			self.log_file = ""
			self.valid_configs = False   # To indicate if all the config 
			# informations recorded are valid or not
			
		def get_twr_ser_port(self):
			""" Returns the serial port for tower """
			return (self.twr_ser_port)
			
		def set_twr_ser_port(self, port_name):
			""" Sets the serial port for communicating with tower. Raises 
			ValueError exception is port is not of type string """
			
			if type(port_name) != type (""):
				raise ValueError, "set_twr_ser_port() excepts a string argument \
				"""
			
			self.twr_ser_port = port_name
			
		def get_dmm_ser_port(self):
			""" Returns the serial port name for communicating with the DMM """
			return (self.dmm_ser_port)
			
		def set_dmm_ser_port(self, port_name):
			""" Sets the serial port name for the communication with the DMMM
			raises ValueError in case of wrong arg """
			if type(port_name) != type(""):
				raise ValueError, "set_dmm_ser_port() excepts a string arg "
				
			self.dmm_ser_port = port_name
			
		def set_cmd_file(self, file_name):
			""" sets a file name for cmds file. Raises ValuError if file_name 
			is not string  """
			if type(file_name) != type(""):
				raise ValueError, "set_cmd_file() requires a string arg "
			self.cmd_file = file_name
			
		def get_cmd_file(self):
			""" Returns a string, self.cmd_file """
			return (self.cmd_file)
			
		def set_log_file(self, file_name):
			""" Sets a file name for the logging of files. Raises ValueError if
			file_name is not of type string """
			if type(file_name) != type(""):
				raise ValueError, "set_log_file(): Requires a string arg "
				
			self.log_file = file_name
			
		def get_log_file(self):
			""" Returns the log file path value """
			return (self.log_file)
			
		def set_valid_configs(self, val):
			""" Sets valid_config parameter to true or false """
			if type(val) == type(False):
				self.valid_configs = val
			elif type(val) == type(1):
				if val == 0:
					self.valid_configs = False
				else:
					self.valid_configs = True
					
		def get_valid_configs(self):
			""" Returns the value of 'valid_config' which is of type boolean"""
			return (self.valid_configs)
			
			
			
		
	
if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = GraphFrame('TWR LTC Demo')
    app.frame.Show()
    app.MainLoop()
