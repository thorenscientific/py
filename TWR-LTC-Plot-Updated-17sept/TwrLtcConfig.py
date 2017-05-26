#-------------------------------------------------------------------------------
# Name:        TwrLtcConfig.py
# Purpose:     A wx frame for configuring the TWR LTC demo
#
# Author:      Navin
#
# Created:     15/07/2011
# Copyright:   (c)MDN
# Licence:     MDN licence
#-------------------------------------------------------------------------------
#!/usr/bin/env python


import wx
from SerialPort import SerialPort
import os


###########################################################################
## Class ConfigFrame
###########################################################################

class ConfigFrame ( wx.Dialog ):
	
	def __init__( self, parent, config_info):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"TWR-LTC demo config", pos = wx.DefaultPosition, size = wx.Size( 302,439 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL, name = u"twrLtc" )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizerMain = wx.BoxSizer( wx.VERTICAL )
		
		self.MainPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerVBox1 = wx.BoxSizer( wx.VERTICAL )
		
		self.stSerPortTwr = wx.StaticText( self.MainPanel, wx.ID_ANY, u"Select a serial port for communicating with the Tower:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stSerPortTwr.Wrap( -1 )
		bSizerVBox1.Add( self.stSerPortTwr, 0, wx.ALL, 15 )
		
		cbTwrSerPortChoices = []
		self.cbTwrSerPort = wx.ComboBox( self.MainPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, cbTwrSerPortChoices, 0 )
		bSizerVBox1.Add( self.cbTwrSerPort, 0, wx.ALL, 10 )
		
		self.stSerPortDmm = wx.StaticText( self.MainPanel, wx.ID_ANY, u"Select a serial port for communicating with the DMM:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stSerPortDmm.Wrap( -1 )
		bSizerVBox1.Add( self.stSerPortDmm, 0, wx.ALL, 15 )
		
		cbDmmSerPortChoices = []
		self.cbDmmSerPort = wx.ComboBox( self.MainPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, cbDmmSerPortChoices, 0 )
		bSizerVBox1.Add( self.cbDmmSerPort, 0, wx.ALL, 10 )
		
		self.stCmdFile = wx.StaticText( self.MainPanel, wx.ID_ANY, u"Select a command file:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stCmdFile.Wrap( -1 )
		bSizerVBox1.Add( self.stCmdFile, 0, wx.ALL, 15 )
		
		self.fpCmdsFile = wx.FilePickerCtrl( self.MainPanel, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.txt", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
		bSizerVBox1.Add( self.fpCmdsFile, 0, wx.ALL, 10 )
		
		self.stLogFile = wx.StaticText( self.MainPanel, wx.ID_ANY, u"Select a file to log data", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stLogFile.Wrap( -1 )
		bSizerVBox1.Add( self.stLogFile, 0, wx.ALL, 15 )
		
		self.fpLogFile = wx.FilePickerCtrl( self.MainPanel, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.csv", wx.DefaultPosition, wx.DefaultSize, wx.FLP_USE_TEXTCTRL | wx.FLP_SAVE )
		bSizerVBox1.Add( self.fpLogFile, 0, wx.ALL, 10 )
		
		BtnsBox = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btnOk = wx.Button( self.MainPanel, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		BtnsBox.Add( self.btnOk, 0, wx.ALIGN_BOTTOM|wx.ALL, 15 )
		
		self.btnCancel = wx.Button( self.MainPanel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		BtnsBox.Add( self.btnCancel, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 15 )
		
		bSizerVBox1.Add( BtnsBox, 1, wx.ALIGN_RIGHT, 15 )
		
		self.MainPanel.SetSizer( bSizerVBox1 )
		self.MainPanel.Layout()
		bSizerVBox1.Fit( self.MainPanel )
		bSizerMain.Add( self.MainPanel, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.SetSizer( bSizerMain )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.cbTwrSerPort.Bind( wx.EVT_TEXT, self.OncbTwrSerPort )
		self.cbDmmSerPort.Bind( wx.EVT_TEXT, self.OncbDmmSerPorts )
		self.fpCmdsFile.Bind( wx.EVT_FILEPICKER_CHANGED, self.OnCmdFileSel )
		self.fpLogFile.Bind( wx.EVT_FILEPICKER_CHANGED, self.OnLogFileSel )
		self.btnOk.Bind( wx.EVT_BUTTON, self.OnOk )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		
		self.init_after()
		self.config = config_info
	
	def __del__( self ):
		pass

	def init_after(self):
		""" This method intializes things specific to this frame """
		port_lister = GetSerPorts()
		ports = port_lister.get_ports()
		for i in ports:
			self.cbTwrSerPort.Append(i)
			self.cbDmmSerPort.Append(i)	
			
	
	# Virtual event handlers, overide them in your derived class
	def OncbTwrSerPort( self, event ):
		event.Skip()
	
	def OncbDmmSerPorts( self, event ):
		event.Skip()
	
	def OnCmdFileSel( self, event ):
		cmd_file = self.fpCmdsFile.GetPath().encode('ASCII')
		if os.path.exists(cmd_file) == True:
			self.config.set_cmd_file(cmd_file)
		else:
			self.config.set_cmd_file("")
			wx.MessageBox("Please enter a valid path for command file ")
			return 
	
	def OnLogFileSel( self, event ):
		log_file = self.fpLogFile.GetPath().encode('ASCII')
		try:
			f = open(log_file, 'wt')
			f.close()
			self.config.set_log_file(log_file)
		except IOError:
			self.config.set_log_file("")
			wx.MessageBox("Please enter a valid path for log file ")
			return 
	
	def OnOk( self, event ):
		""" Clicked on OK """
		twr_ser = self.cbTwrSerPort.GetValue().encode('ASCII')
		
		
		if twr_ser == "":
			wx.MessageBox("Please enter an valid serial port name for \
			communicating with the tower ")
			self.set_invalid()
			return 
		else:
			try:
				ser = SerialPort(twr_ser)
				ser.write_to_port('X0')  # Write some known command for a check
				read_info = ser.read_from_twr()
				if read_info[1] == False:
					dlg = wx.MessageDialog(self, "The Tower did not respond with expected response."+ \
					" Please make sure that you have selected appropriate port."+ \
					"\n\n Do you want to retry with a different serial port ?", \
					"Warning",
					wx.YES_NO)
					
					resp = dlg.ShowModal()
					dlg.Destroy()
					if resp == wx.ID_YES:
						ser.close_port()
						self.set_invalid()
						return 
				else:
					self.config.set_twr_ser_port(twr_ser)	
					ser.close_port()
			except IOError:
				wx.MessageBox("Could not open com port %s ", twr_ser)
				self.set_invalid()
				return  
				
			dmm_ser = self.cbDmmSerPort.GetValue().encode('ASCII')
			
			if dmm_ser == "":
				wx.MessageBox("Please enter an valid serial port name for \
			communicating with the DMM ")
				self.set_invalid()
				return
			else:
				try:
					ser = SerialPort(dmm_ser, '9600', '2')
					read_info = ser.read_from_dmm()
				
						
					if read_info[1] == False :
						dlg = wx.MessageDialog(self, "The dmm did not respond with expected response."+ \
						" Please make sure that you have selected appropriate port."+ \
						" And that the DMM has been set up properly " + \
						"\n\n Do you want to retry with a different serial port ?", \
						"Warning",
						wx.YES_NO)
					
						resp = dlg.ShowModal()
						dlg.Destroy()
						if resp == wx.ID_YES:
							ser.close_port()
							self.set_invalid()
							return 
					else:
						self.config.set_dmm_ser_port(dmm_ser)
						ser.close_port()	
				except IOError:
					wx.MessageBox("Could not open com port %s ", twr_ser)
					self.set_invalid()
					return  
				
					 
		if dmm_ser == twr_ser:
			# can't use same port for both DMM and Tower	
			wx.MessageBox("Cannot use same port for communicating with both \n"+
			"Tower and DMM ")
			self.set_invalid()
			return  
				
		# Let us validate the exstince of the command file
		
		if os.path.exists(self.config.get_cmd_file()) == False:
			wx.MessageBox("Please enter a valid path for command file ")
			self.set_invalid()
			return 
			
		if os.path.exists(self.config.get_log_file()) == False:
			wx.MessageBox("Please enter a valid path for log file ")
			self.set_invalid()
			return
					
		# if we have made it to this point, most of the things are valid
		# except for the serial ports which are dependent on user choice(s)
		
		self.set_valid()	
		self.Close()			
					 
	
	def set_valid(self):
		""" This method sets the valid field of configuartion to True """
		self.config.valid_configs = True	
		
	def set_invalid(self):
		""" This method sets the valid field of configuartion to False """
		self.config.valid_configs = False			
	
	def OnCancel( self, event ):
		self.config.set_valid_configs(False)
		self.Close()
	


class GetSerPorts:
	""" This class tries to scan all the ports and lists them """
	def __init__(self):
		""" Initializer, determines the os and tries to select a prefix name 
		for serial port """
		if os.name == 'nt':
			self.port_name = 'COM'
			self.offset = 1
		elif os.name == 'posix':
			self.port_name = '/dev/ttyUSB'
			self.offset = 0
		else:
			self.port_name = ''
			self.offset = 0
		
	
	def get_ports(self):
		""" This method returns a list of all the available serial ports """
		ports  = []
		import serial
		
		for i in range(70):
			try:
				ser = serial.Serial(i)
				ports.append(self.port_name + str(i+self.offset))
				ser.close()
			except serial.SerialException:
				pass
		return ports
		 		
	
