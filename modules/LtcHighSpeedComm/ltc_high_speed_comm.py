"""This module is a wrapper around the LtcHighSpeedComm.dll

It provides a class and some constants used to communicate with high-speed
Linear Technology devices using an off-the-shelf FPGA demo-board and an LTC
communication interface board. It requires the FPGA be loaded with an LTC 
bit-file and allows high-speed data transfer, SPI communication and FPGA
configuration. Note that there is no open command, the device is opened
automatically as needed. There is a close method, but it is not necessary to
call it, the cleanup method will close the handle. If there is an error or the
close method is called, the device will again be opened automatically as 
needed. Methods will raise a ValueError if the arguments don't make sense, all
other errors will cause a HighSpeedCommError to be raised.
To connect do something like this:
    import ltc_high_speed_comm as lths
        
    device_info = None
    for info in lths.list_devices():
        # if you know the serial number you want, you could check that here
        if info.get_description() == "LTC Communication Interface2":
            # you could use a with statement like the one below to open the
            # device and query it to make sure it is the one you want here
            device_info = info
            break
    if device_info is None:
        raise Exception("could not find compatible device")
        
    serial_number = device_info.get_serial_number()
    print serial_number
    
    # open and use the device
    with lths.Lths(device_info) as device:
        device.set_bit_mode(lths.MODE_MPSSE)
        device.gpio_write_high_byte(0xFF)
"""

import ctypes as ct
import atexit

#: mode argument to set_mode. For FIFO communication use MODE_FIFO, for
#: everything else use MODE_MPSSE
MODE_MPSSE = 0x02
MODE_FIFO  = 0x40

#: mode argument to spi_set_mode, if you are not sure, you probably want
#: SPI_MODE_0
SPI_MODE_0 = 0
SPI_MODE_2 = 2

#: pin_state argument to spi_set_chip_select and fpga_set_reset
PIN_STATE_LOW = 0
PIN_STATE_HIGH = 1

ERROR_BUFFER_SIZE = 256
SERIAL_NUMBER_BUFFER_SIZE = 16
DESCRIPTION_BUFFER_SIZE = 64

# non-public method to map a type string to the appropriate c_types type
def _ctype_from_string(type):
    if type == "ubyte":
        return ct.ubyte
    elif type == "uint16":
        return ct.uint16
    elif type == "uint32":
        return ct.uint32
    else:
        raise ValueError("Invalid type string")

class HighSpeedCommError(Exception):
    """Represents errors returned by the native LtcHighSpeedComm.dll"""
    pass

class DeviceInfo(ct.Structure):
    """Device info returned by list_devices"""
    _fields_ = [
        ("_indices", ct.c_long * 2),
        ("_serial_number", ct.c_char * SERIAL_NUMBER_BUFFER_SIZE),
        ("_description", ct.c_char * DESCRIPTION_BUFFER_SIZE)
    ]
    def get_serial_number(self):
        return self._serial_number[:SERIAL_NUMBER_BUFFER_SIZE]
    def get_description(self):
        return self._description[:DESCRIPTION_BUFFER_SIZE]
    
# non-public DLL loading stuff
_dll_handle = ct.windll.kernel32.LoadLibraryA("LtcHighSpeedComm.dll")
_dll = ct.CDLL(None, handle=_dll_handle)
# non-public DLL cleanup stuff
def _cleanup(dll, dll_handle, free_function):
    del dll
    free_function(dll_handle)
atexit.register(_cleanup, _dll, _dll_handle, ct.windll.kernel32.FreeLibrary)
    
def list_devices():
    num_devices = ct.c_int()
    if _dll.LthsCreateDeviceList(ct.byref(num_devices)) != 0:
        raise HighSpeedCommError("Could not create device info list")
    device_info_list = (DeviceInfo * num_devices.value)()
    if _dll.LthsGetDeviceList(device_info_list, num_devices) != 0:
        raise HighSpeedCommError(
            "Could not get device info list, or no device found")
    return device_info_list
    
class Lths(object):
    """This class wraps up the interface to the native DLL.
    
    It manages references to LthsHandle and LthsFindInfo and makes all their
    functions available as methods.
    """
 
    def __init__(self, device_info):
        """Initialize fields and find first available high-speed device.
        
        Note that this function will find any FT2232H based device, it may be
        necessary to query the device for more information to determine if it
        is the desired device.
        """
        self._handle = ct.c_void_p(None)
        self._c_error_buffer = ct.create_string_buffer(ERROR_BUFFER_SIZE)
        self._c_array = None
        self._c_array_type = "none"
        if _dll.LthsInitDevice(ct.byref(self._handle), device_info) != 0:
            raise HighSpeedCommError("Error initializing the device")
        
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.cleanup()

    # raise an exception if the return code indicates an error
    def _raise_on_error(self, error_code):
        if (error_code != 0):
            _dll.LthsGetErrorInfo(self._handle, self._c_error_buffer, ERROR_BUFFER_SIZE)
            raise HighSpeedCommError(self._c_error_buffer.value)

    def cleanup(self):
        """Clean up (close and delete) all resources."""
        if self._handle is not None:
            _dll.LthsCleanup(self._handle)
            self._handle = None

    def get_serial_number(self):
        """Return the current device's serial number."""
        c_serial_number = ct.create_string_buffer(SERIAL_NUMBER_BUFFER_SIZE)
        self._raise_on_error(_dll.LthsGetSerialNumber(self._handle, c_serial_number,
            SERIAL_NUMBER_BUFFER_SIZE))
        return c_serial_number.value

    def get_description(self):
        """Return the current device's description."""
        c_description = ct.create_string_buffer(DESCRIPTION_BUFFER_SIZE)
        self._raise_on_error(_dll.LthsGetDescription(self._handle, c_description,
            DESCRIPTION_BUFFER_SIZE))
        return c_description.value

    def set_timeouts(self, read_timeout, write_timeout):
        """Set read and write time-outs."""
        c_read_timeout = ct.c_int(read_timeout)
        c_write_timeout = ct.c_int(write_timeout)
        self._raise_on_error(_dll.LthsSetTimeouts(self._handle, c_read_timeout,
            c_write_timeout))

    def set_bit_mode(self, mode):
        """Set device mode to MODE_FIFO or MODE_MPSSE."""
        c_mode = ct.c_int(mode)
        self._raise_on_error(_dll.LthsSetBitMode(self._handle, c_mode))
        
    def purge_io(self):
        """Purge input and output buffers."""
        self._raise_on_error(_dll.LthsPurgeIo(self._handle))
        
    def close(self):
        """Close device. Device will be automatically re-opened when needed."""
        self._raise_on_error(_dll.LthsClose(self._handle))
        
    # send fifo data of various types
    def _fifo_send_by_type(self, type, values, start, end):
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        if end <= start:
            raise ValueError("end must be > start")
        
        num_values = end - start
        
        if self._c_array_type != type or len(self._c_array) < num_values:
            self._c_array = (_ctype_from_string(type) * num_values)()
        
        for i in xrange(0, num_values):
            self._c_array[i] = values[i+start]
            
        c_num_values = ct.c_int(num_values)
        c_num_transfered = ct.c_int()
        if type == "ubyte":
            self._raise_on_error(_dll.LthsFifoSendBytes(self._handle, self._c_array,
            c_num_values, ct.byref(c_num_transfered)))
        elif type == "uint16":
            self._raise_on_error(_dll.LthsFifoSendUint16Values(self._handle, self._c_array,
            c_num_values, ct.byref(c_num_transfered)))
        elif type == "uint32":
            self._raise_on_error(_dll.LthsFifoSendUint16Values(self._handle, self._c_array,
            c_num_values, ct.byref(c_num_transfered)))
        else:
            raise ValueError("type string must be ubyte, uint16 or uint32")
        
        return c_num_transfered.value
        
    def fifo_send_bytes(self, values, start=0, end=-1):
        """Send elements of values[start:end] as bytes via FIFO.
        
        Defaults for start and end and interpretation of negative values is
        the same as for slices.
        """
        return self.fifo_send_by_type("ubyte", values, start, end)
    def fifo_send_uint16_values(self, values, start=0, end=-1):
        """Send elements of values[start:end] as 16-bit values via FIFO.
        
        Defaults for start and end and interpretation of negative values is
        the same as for slices.
        """
        return self.fifo_send_by_type("uint16", values, start, end)
    def fifo_send_uint32_values(self, values, start=0, end=-1):
        """Send elements of values[start:end] as 32-bit values via FIFO.
        
        Defaults for start and end and interpretation of negative values is
        the same as for slices.
        """
        return self.fifo_send_by_type("uint32", values, start, end)
        
    # receive FIFO data of various types
    def _fifo_receive_by_type(self, type, values, start, end):
        if values is None and end < 0:
            raise ValueError("If values is None, end cannot be negative")
        if (values is None and start != 0):
            raise ValueError("If values is None, start must be 0")
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        if end <= start:
            raise ValueError("end must be > start")    
        
        num_values = end - start
              
        if self._c_array_type != type or len(self._c_array) < num_values:
            self._c_array = (_ctype_from_string(type) * num_values)()
        
        c_num_values = ct.c_int(num_values)
        c_num_transfered = ct.c_int()
        if type == "ubyte":
            self._raise_on_error(_dll.LthsFifoReceiveBytes(self._handle, self._c_array,
                c_num_values, ct.byref(c_num_transfered)))
        elif type == "uint16":
            self._raise_on_error(_dll.LthsFifoReceiveUint16Values(self._handle,
                self._c_array, c_num_values, ct.byref(c_num_transfered)))
        elif type == "uint32":
            self._raise_on_error(_dll.LthsFifoReceiveUint16Values(self._handle, 
                self._c_array, c_num_values, ct.byref(c_num_transfered)))
        else:
            raise ValueError("type string must be 'ubyte', 'uint16' or 'uint32'")
        
        if values is None:
            values = [self._c_array[i + start] for i in xrange(0, num_values)]
        else:
            for i in xrange(0, num_values):
                values[i + start] = int(self._c_array[i])
        
        return (c_num_transfered.value, values)
        
    def fifo_receive_bytes(self, values=None, start=0, end=-1):
        """Fill values[start:end] with bytes received via FIFO.
        
        If values is None (default) create a new list. Defaults for start and
        end and interpretation of negative values is the same as for slices.
        Return a reference to values.
        """
        return self._fifo_receive_by_type("ubyte", values, start, end)
    
    def fifo_receive_uint16_values(self, values=None, start=0, end=-1):
        """Fill values[start:end] with 16-bit values received via FIFO.
        
        If values is None (default) create a new list. Defaults for start and
        end and interpretation of negative values is the same as for slices.
        Return a reference to values.
        """
        return self._fifo_receive_by_type("uint16", values, start, end)
    
    def fifo_receive_uint32_values(self, values=None, start=0, end=-1):
        """Fill values[start:end] with 32-bit values received via FIFO.
        
        If values is None (default) create a new list. Defaults for start and
        end and interpretation of negative values is the same as for slices.
        Return a reference to values.
        """
        return self._fifo_receive_by_type("uint32", values, start, end)
        
    def spi_set_mode(self, mode):
        """Set the SPI mode (if never called, mode is MODE_0)."""
        c_mode = ct.c_int(mode)
        self._raise_on_error(_dll.LthsSpiSetMode(self._handle, c_mode))
        
    def spi_send_byte(self, value):
        """Send a byte via SPI."""
        c_value = ct.c_ubyte(value)
        self._raise_on_error(_dll.LthsSpiSendByte(self._handle, c_value))
        
    def spi_send_bytes(self, values, start=0, end=-1):
        """Send elements of values[start:end] as via SPI.
        
        Defaults for start and end and interpretation of negative values is
        the same as for slices.
        """
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        elif end < start:
            raise ValueError("end must be >= start")
            
        num_values = end - start
        
        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
            
        for i in xrange(0, num_values):
            self._c_array[i] = values[i+start]
            
        c_num_values = ct.c_int(num_values)
        self._raise_on_error(_dll.LthsSpiSendBytes(self._handle, self._c_array,
            c_num_values))
    
    def spi_receive_byte(self):
        """Receive a byte via SPI and return it"""
        c_value = ct.c_int()
        self._raise_on_error(_dll.LthsSpiReceiveByte(self._handle, ct.byref(c_value)))
        return c_value.value
        
    def spi_receive_bytes(self, values=None, start=0, end=-1):
        """Fill values[start:end] with bytes received via SPI.
        
        If values is None (default) create a new list. Defaults for start and
        end and interpretation of negative values is the same as for slices.
        Return a reference to values.
        """
        if values is None and end < 0:
            raise ValueError("If values is None, end cannot be -1")
        if values is None and start != 0:
            raise ValueError("If values is None, start must be 0")
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        elif end < start:
            raise ValueError("end must be >= start")   
            
        num_values = end - start
        
        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
        
        c_num_values = ct.c_int(num_values)
        self._raise_on_error(_dll.LthsSpiReceiveBytes(self, self._c_array, c_num_values))
        
        if values is None:
            values = [self._c_array[i + start] for i in xrange(0, num_values)]
        else:
            for i in xrange(0, num_values):
                values[i + start] = int(self._c_array[i])
        
        return values
        
    def spi_transceive_byte(self, send_value):
        """Send and receive a byte via SPI and return the received byte."""
        c_send_value = ct.c_ubyte(send_value)
        c_receive_value = ct.c_ubyte()
        self._raise_on_error(_dll.LthsSpiTransceiveByte(self._handle,
            c_send_value, ct.byref(c_receive_value)))
        return c_receive_value.value
    
    def spi_transceive_bytes(self, send_values, send_start=0, send_end=-1, 
            receive_values=None, receive_start=0, receive_end=-1):
        """Transceive bytes via SPI.
        
        Simultaneously send send_values[send_start:send_end] and fill 
        receive_values[receive_start:receive_end] with bytes received via
        SPI. If receive_values is None (default) create a new list. Defaults
        for (send_/receive_)start and (send_/receive_)end and interpretation
        of negative values is the same as for slices. Return a reference to
        values.
        """ 
        if send_start < 0:
            raise ValueError("send_start must be >= 0")
        if send_end < 0:
            send_end = len(send_values) + send_end + 1
        if send_end < send_start:
            raise ValueError("send_end must be >= send_start")
            
        num_values = send_end - send_start
        
        if receive_values is None and receive_end < 0:
            raise ValueError("If receive_values is None, "
                "receive_end cannot be -1")
        if receive_start <= 0:
            raise ValueError("receive_start must be > 0")
        if receive_end < 0:
            receive_end = len(receive_values) + receive_end + 1
        if receive_end <= receive_start:
            raise ValueError("receive_end must be > receive_start")    
        if num_values != receive_end - receive_start:
            raise ValueError("send_end-send_start must be equal to " +
                "receive_end-receive_start")
        
        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
        for i in xrange(0, num_values):
            self._c_array[i] = send_values[i+send_start]

        c_num_values = ct.c_int(num_values)
        self._raise_on_error(_dll.LthsSpiTransceiveBytes(self, self._c_array, 
            self._c_array, c_num_values))
            
        if receive_values is None:
            receive_values = [self._c_array[i + receive_start] for i in xrange(0, num_values)]
        else:
            for i in xrange(0, num_values):
                receive_values[i + receive_start] = int(self._c_array[i])
        
        return receive_values
        
    def spi_send_byte_at_address(self, address, num_address_bytes, value):
        """Write an address and a value via SPI.
        
        Many SPI devices adopt a convention similar to I2C addressing, where a
        byte is sent indicating which register address the rest of the data
        pertains to. Often there is a read-write bit in the address, this
        function will not shift or set any bits in the address, it basically
        just write two bytes, the address byte and data byte one after the
        other. The address can be 1, 2 or 4 bytes wide, num_address_bytes 
        indicates the width of the address (1 is default).
        """
        c_address = ct.c_uint32(address)
        c_num_address_bytes = ct.c_int(num_address_bytes)
        c_value = ct.c_ubyte(value)
        self._raise_on_error(_dll.LthsSpiSendByteAtAddress(self._handle, c_address,
            c_num_address_bytes, c_value))
        
    def spi_send_bytes_at_address(self, address, num_address_bytes, values,
            start=0, end=-1):
        """Write an address byte and values[start:end] via SPI.
        
        Many SPI devices adopt a convention similar to I2C addressing, where a
        byte is sent indicating which register address the rest of the data
        pertains to. Often there is a read-write bit in the address, this
        function will not shift or set any bits in the address, it basically
        just write two bytes, the address byte and data byte one after the
        other. The address can be 1, 2 or 4 bytes wide, num_address_bytes 
        indicates the width of the address (1 is default). Defaults for start
        and end and interpretation of negative values is the same as for
        slices.
        """        
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        elif end < start:
            raise ValueError("end must be >= start")
            
        num_values = end - start
        
        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
        for i in xrange(0, num_values):
            self._c_array[i] = values[i+start]
        
        c_num_values = ct.c_int(num_values)
        c_address = ct.c_uint32(address)
        c_num_address_bytes = ct.c_int(num_address_bytes)
        self._raise_on_error(_dll.LthsSpiSendBytesAtAddress(self._handle, c_address,
            c_num_address_bytes, self._c_array, c_num_values))
    
    def spi_receive_byte_at_address(self, address, num_address_bytes=1):
        """Write an address and receive a value via SPI; return the value.
        
        Many SPI devices adopt a convention similar to I2C addressing, where a
        byte is sent indicating which register address the rest of the data
        pertains to. Often there is a read-write bit in the address, this
        function will not shift or set any bits in the address, it basically
        just write two bytes, the address byte and data byte one after the
        other. The address can be 1, 2 or 4 bytes wide, num_address_bytes 
        indicates the width of the address (1 is default).
        """
        c_address = ct.c_uint32(address)
        c_num_address_bytes = ct.c_int(num_address_bytes)
        c_value = ct.c_ubyte()
        self._raise_on_error(_dll.LthsSpiReceiveByteAtAddress(self._handle, 
            c_address, c_num_address_bytes, ct.byref(c_value)))
        return c_value.value
        
    def spi_receive_bytes_at_address(self, address, num_address_bytes=1, values=None, 
            start=0, end=-1):
        """Fill values[start:end] with values received via SPI at an address.
        
        Many SPI devices adopt a convention similar to I2C addressing, where a
        byte is sent indicating which register address the rest of the data
        pertains to. Often there is a read-write bit in the address, this
        function will not shift or set any bits in the address, it basically
        just write two bytes, the address byte and data byte one after the
        other. The address can be 1, 2 or 4 bytes wide, num_address_bytes 
        indicates the width of the address (1 is default). Defaults for start
        and end and interpretation of negative values is the same as for
        slices. if values is None a new list is created. A reference to values
        is returned.
        """      
        if values is None and end < 0:
            raise ValueError("If values is None, end cannot be -1")
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        elif end < start:
            raise ValueError("end must be >= start")
        
        num_values = end - start

        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
        
        c_num_values = ct.c_int(num_values)
        c_address = ct.c_uint32(address)
        c_num_address_bytes = ct.c_int(num_address_bytes)
        self._raise_on_error(_dll.LthsSpiReceiveBytesAtAddress(self, c_address,
            c_num_address_bytes, self._c_array, c_num_values))
        
        if values is None:
            values = [self._c_array[i + start] for i in xrange(0, num_values)]
        else:
            for i in xrange(0, num_values):
                values[i + start] = int(self._c_array[i])
        
        return values
        
    def spi_set_chip_select(self, pin_state):
        """Set the SPI chip-select high or low."""
        c_pin_state = ct.int(pin_state)
        self._raise_on_error(_dll.LthsSpiSetChipSelect(self._handle, c_pin_state))
        
    def spi_send_no_chip_select(self, values, start=0, end=-1):
        """Send values[start:end] via SPI without controlling chip-select.
        Defaults for start and end and interpretation of negative values is
        the same as for slices.
        """
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        elif end < start:
            raise ValueError("end must be >= start")
            
        num_values = end - start
        
        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
            
        for i in xrange(0, num_values):
            self._c_array[i] = values[i+start]
            
        c_num_values = ct.c_int(num_values)
        self._raise_on_error(_dll.LthsSpiSendBytesNoChipSelect(self._handle, self._c_array,
            c_num_values))
            
    def spi_receive_no_chip_select(self, values=None, start=0, end=-1):
        """Fill values[start:end] via SPI without controlling chip-select.
        
        If values is None a new list is created. Defaults for start and end
        and interpretation of negative values is the same as for slices. A
        reference to values is returned.
        """
        if values is None and end < 0:
            raise ValueError("If values is None, end cannot be -1")
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        elif end < start:
            raise ValueError("end must be >= start")   
            
        num_values = end - start
        
        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
        
        c_num_values = ct.c_int(num_values)
        self._raise_on_error(_dll.LthsSpiReceiveBytesNoChipSelect(self, self._c_array,
            c_num_values))
        
        if values is None:
            values = [self._c_array[i + start] for i in xrange(0, num_values)]
        else:
            for i in xrange(0, num_values):
                values[i + start] = int(self._c_array[i])
        
        return values
    
    def spi_transceive_no_chip_select(self, send_values, send_start=0, send_end=-1,
            receive_values=None, receive_start=0, receive_end=-1):
        """Transceive bytes without controlling chip-select.
        
        Simultaneously send send_values[send_start:send_end] and fill 
        receive_values[receive_start:receive_end] with bytes received via
        SPI. If receive_values is None (default) create a new list. Defaults
        for (send_/receive_)start and (send_/receive_)end and interpretation
        of negative values is the same as for slices. Return a reference to
        values.
        """ 
        if send_start < 0:
            raise ValueError("send_start must be >= 0")
        if send_end < 0:
            send_end = len(send_values) + send_end + 1
        if send_end <= send_start:
            raise ValueError("send_end must be > send_start")
            
        num_values = send_end - send_start
        
        if receive_values is None and send_end < 0:
            raise ValueError("If receive_values is None, receive_end cannot be -1")
        if receive_start < 0:
            raise ValueError("receive_start must be >= 0")
        if receive_end < 0:
            receive_end = len(receive_values) + receive_end + 1
        elif receive_end < receive_start:
            raise ValueError("receive_end must be >= receive_start")    
        if num_values != receive_end - receive_start:
            raise ValueError("send_end-send_start must be equal to" + 
                "receive_end-receive_start")
        
        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
        for i in xrange(0, num_values):
            self._c_array[i] = send_values[i+send_start]

        c_num_values = ct.c_int(num_values)
        self._raise_on_error(_dll.LthsSpiTransceiveBytesNoChipSelect(self, 
            self._c_array, self._c_array, c_num_values))
            
        if receive_values is None:
            receive_values = [self._c_array[i + receive_start] for i in xrange(0, num_values)]
        else:
            for i in xrange(0, num_values):
                receive_values[i + receive_start] = int(self._c_array[i])
        
        return receive_values
        
    def fpga_set_reset(self, pin_state):
        """Set the FPGA reset bit high or low."""
        c_pin_state = ct.c_int(pin_state)
        self._raise_on_error(_dll.LthsFpgaSetReset(self._handle, c_pin_state))
        
    def fpga_write_address(self, address):
        """Set the FPGA address to write or read."""
        c_address = ct.ubyte(address)
        self._raise_on_error(_dll.LthsFpgaWriteAddress(self._handle, c_address))
        
    def fpga_write_data(self, value):
        """Write a value to the current FPGA address."""
        c_value = ct.ubyte(value)
        self._raise_on_error(_dll.LthsFpgaWriteData(self._handle, c_value))
        
    def fpga_read_data(self):
        """Read a value from the current FPGA address and return it."""
        c_value = ct.ubyte()
        self._raise_on_error(_dll.LthsFpgaReadData(self._handle, ct.byref(c_value)))
        return c_value.value
        
    def fpga_write_data_at_address(self, address, value):
        """Set the current address and write a value to it."""
        c_address = ct.ubyte(address)
        c_value = ct.ubyte(value)
        self._raise_on_error(_dll.LthsFpgaWriteDataAtAddress(self._handle, c_address,
            c_value))
            
    def fpga_read_data_at_address(self, address):
        """Set the current address and read a value from it."""
        c_address = ct.ubyte(address)
        c_value = ct.ubyte()
        self._raise_on_error(_dll.LthsFpgaReadDataAtAddress(self._handle, c_address,
            ct.byref(c_value)))
        return c_value.value
        
    def gpio_write_high_byte(self, value):
        """Set the GPIO high byte to a value."""
        c_value = ct.c_ubyte(value)
        self._raise_on_error(_dll.LthsGpioWriteHighByte(self._handle, c_value))
        
    def gpio_read_high_byte(self):
        """Read the GPIO high byte and return the value."""
        c_value = ct.ubyte()
        self._raise_on_error(_dll.LthsGpioReadHighByte(self._handle, ct.byref(c_value)))
        return c_value.value
        
    def gpio_write_low_byte(self, value):
        """Set the GPIO low byte to a value."""
        c_value = ct.ubyte(value)
        self._raise_on_error(_dll.LthsGpioWriteLowByte(self._handle, c_value))
        
    def gpio_read_low_byte(self):
        """Read the GPIO low byte and return the value"""
        c_value = ct.ubyte()
        self._raise_on_error(_dll.LthsGpioReadLowByte(self._handle, ct.byref(c_value)))
        return c_value.value
        
    def fpga_i2c_set_bit_bang_register(self, register_address):
        """Set the FPGA register used to do bit-banged I2C.
        
        If not called, address used is 0x11.
        """
        c_register_address = ct.ubyte(register_address)
        self._raise_on_error(_dll.LthsFpgaI2cSetBitBangRegister(self._handle,
            c_register_address))
            
    def fpga_i2c_send_byte(self, address, value):
        """Send a value to an address over bit-banged I2C via FPGA register.
        
        address must be a 7-bit address, it will be left shifted internally.
        """
        c_address = ct.ubyte(address)
        c_value = ct.ubyte(value)
        self._raise_on_error(_dll.LthsFpgaI2cSendByte(self._handle, c_address, c_value))
        
    def fpga_i2c_send_bytes(self, address, values, start=0, end=-1):
        """Send values to an address over bit-banged I2C via FPGA register.
        
        address must be a 7-bit address, it will be left shifted internally.
        Defaults for start and end and interpretation of negative values is
        the same as for slices.
        """
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        elif end < start:
            raise ValueError("end must be >= start")
            
        num_values = end - start
        
        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
        for i in xrange(0, num_values):
            self._c_array[i] = values[i+start]
        
        c_num_values = ct.c_int(num_values)
        c_address = ct.c_uint32(address)
        self._raise_on_error(_dll.LthsFpgaI2cSendBytes(self._handle, c_address,
            self._c_array, c_num_values))
        
    def fpga_i2c_receive_byte(self, address):
        """
        Receive a value from an address over bit-banged I2C via FPGA register.
        
        address must be a 7-bit address, it will be left shifted and the read
        bit will be set internally. The received value is returned.
        """
        c_address = ct.ubyte(address)
        c_value = ct.ubyte()
        self._raise_on_error(_dll.LthsFpgaI2cReceiveByte(self._handle, c_address,
            ct.byref(c_value)))
        return c_value.value
        
    def fpga_i2c_receive_bytes(self, address, values=None, start=0, end=-1):
        """
        Receive values from an address over bit-banged I2C via FPGA register.
        
        address must be a 7-bit address, it will be left shifted and the read
        bit will be set internally. If values is None a new list is created.
        Defaults for start and end and interpretation of negative values is
        the same as for slices. a reference to values is returned.
        """
        if values is None and end < 0:
            raise ValueError("If values is None, end cannot be -1")
        if start < 0:
            raise ValueError("start must be >= 0")
        if end < 0:
            end = len(values) + end + 1
        elif end < start:
            raise ValueError("end must be >= start")
        
        num_values = end - start

        if self._c_array_type != "ubyte" or len(self._c_array) < num_values:
            self._c_array = (ct.c_ubyte * num_values)()
        
        c_num_values = ct.c_int(num_values)
        c_address = ct.c_uint32(address)
        self._raise_on_error(_dll.LthsFpgaI2cReceiveBytes(self, c_address,
            self._c_array, c_num_values))
        
        if values is None:
            values = [self._c_array[i + start] for i in xrange(0, num_values)]
        else:
            for i in xrange(0, num_values):
                values[i + start] = int(self._c_array[i])
        
        return values
            
    def fpga_i2c_receive_string(self, address, num_chars):
        """
        Receive a string from an address over bit-banged I2C via FPGA register.
        
        address must be a 7-bit address, it will be left shifted and the read
        bit will be set internally. If values is None a new list is created.
        Defaults for start and end and interpretation of negative values is
        the same as for slices. a reference to values is returned.
        """
        c_address = ct.c_uint8(address)
        c_string = ct.create_string_buffer(num_chars)
        self._raise_on_error(_dll.LthsFpgaI2cReceiveString(self._handle, c_address,
            c_string, num_chars))
        return c_string.value
