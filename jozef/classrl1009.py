from ctypes import *
# r=rl1009()
# r.version()
# r.query(5,'*IDN?')
class rl1009:
	def __init__(self, rlib=None):
		if rlib is None:
			self._rlib=windll.REAY_LABS_GPIB
		else:
			self._rlib=rlib
			self.set_terminator()
			self.set_timeouts()
	# would it not be nicer, to have a wrapper,
	# to define the functions, restype, and argtypes
	#def functionWrapper(function,kwrestype, kwargtypes*,arguments**):
	#
	#   functionWrapper(close_connection,c_int,[])
	#   functionWrapper(error_description,c_char_p,[])
	#
	def close_connection(self):
		# public static extern void close_connection()
		self._rlib.close_connection.argtypes=[]
		self._rlib.close_connection.restype=c_int
		return self._rlib.close_connection()

	def connected(self):
		# public static extern bool connected()
		self._rlib.connected.argtypes=[]
		self._rlib.connected.restype=c_int
		return self._rlib.connected()

	def gpib_error(self):
		# public static extern bool gpib_error()
		self._rlib.gpib_error.argtypes=[]
		self._rlib.gpib_error.restype=c_int
		return self._rlib.gpib_error.restype()

	def error_description(self):
		# public static extern string error_description()
		self._rlib.error_description.argtypes=[]
		self._rlib.error_description.restype=c_char_p
		return self._rlib.error_description()

	def device_clear(self,address):
		#public static extern void device_clear(byte address)
		self._rlib.device_clear.argtypes=[c_int]
		self._rlib.device_clear.restype=c_int
		return self._rlib.device_clear(address)

	def get_address(self):
		#public static extern byte get_address()
		self._rlib.get_address.argtypes=[]
		self._rlib.get_address.restype=c_int
		return self._rlib.get_address()

	##### this is not working as intended
	##### this is not working as intended
	##### go over this interface
	##### this is not working as intended
	def get_timeouts(self):
		# public static extern byte get_timeouts(ref int read_timeout, ref int write_timeout)
		r=c_int()
		w=c_int()
		#self._rlib.get_timeouts.argtypes
		self._rlib.get_timeouts.restype=c_int
		self._rlib.get_timeouts(byref(r),byref(w))
		return [r.value, w.value]

	def get_terminator(self):
		#public static extern byte get_terminator()
		self._rlib.get_terminator.argtypes=[]
		self._rlib.get_terminator.restype=c_int
		return self._rlib.get_terminator()

	def group_trigger(self,address_list):
		#public static extern void group_trigger(string address_list)
		self._rlib.group_trigger.argtypes=[c_char_p]
		self._rlib.group_trigger.restype=None
		return self._rlib.group_trigger(address_list)

	def local(self,address):
		#public static extern void local(byte address)
		self._rlib.local.argtypes=[c_int]
		self._rlib.local.restype=None
		return self._rlib.local(address)

	def query(self,address,command):
		#public static extern string query(byte address, string command)
		self._rlib.query.argtypes=[c_int,c_char_p]
		self._rlib.query.restype=c_char_p
		return self._rlib.query(address, command)

	def read(self,address):
		#public static extern string read(byte address)
		self._rlib.read.argtypes=[c_int]
		self._rlib.read.restype=c_char_p
		return self._rlib.read(address)

	def serial_poll(self,address):
		#public static extern byte serial_poll(byte address)
		self._rlib.poll.argtypes=[c_int]
		self._rlib.poll.restype=c_int
		return self._rlib.poll(address)

	def set_address(self,address):
		#public static extern void set_address(byte address)
		self._rlib.set_address.argtypes=[c_int]
		self._rlib.set_address.restype=None
		return self._rlib.set_address(address)

	def set_led_green(self):
		#public static extern void set_led_green(byte address)
		self._rlib.set_led_green.argtypes=[]
		self._rlib.set_led_green.restype=None
		return self._rlib.set_led_green()

	def set_led_off(self):
		#public static extern void set_led_off(byte address)
		self._rlib.set_led_off.argtypes=[]
		self._rlib.set_led_off.restype=None
		return self._rlib.set_led_off()

	def set_led_red(self):
		#public static extern void set_led_red(byte address)
		self._rlib.set_led_red.argtypes=[]
		self._rlib.set_led_red.restype=None
		return self._rlib.set_led_red()

	def set_terminator(self,terminator=1):
		#public static extern void set_terminator(byte terminator);
		self._rlib.set_terminator.argtypes=[c_int]
		self._rlib.set_terminator.restype=None
		return self._rlib.set_terminator(terminator)

	def set_timeouts(self,read_timeout=2000, write_timeout=100):
		#public static extern void set_timeouts(int read_timeout, int write_timeout);
		self._rlib.set_timeouts.argtypes=[c_long,c_long]
		self._rlib.set_timeouts.restype=None
		return self._rlib.set_timeouts(read_timeout, write_timeout)

	def srq_asserted(self):
		#public static extern bool srq_asserted();
		self._rlib.srq_asserted.argtypes=[]
		self._rlib.srq_asserted.restype=[c_int]
		return self._rlib.srq_asserted()

	def version(self):
		#public static extern string version();
		self._rlib.version.argtypes=[]
		self._rlib.version.restype=c_char_p
		return self._rlib.version()

	def write(self,address,command):
		#public static extern void write(byte address, string command);
		self._rlib.write.argtypes=[c_int,c_char_p]
		self._rlib.write.restype=None
		return self._rlib.write(address, command)


