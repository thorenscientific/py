import ctypes
import os

class FTSyncFifoDevice():
    def __init__(self):           
        self.device = None
        self.MaxErrChars = ctypes.c_int(112)
        self.errBuff = ctypes.create_string_buffer(self.MaxErrChars.value)
        
        self.ModeMPSSE = 0
        self.ModeFIFO = 1
        self.PinStateLow = 0
        self.PinStateHigh = 1
        
        # load the library
        library = 'FTSyncFifoDevice.dll'
        path = os.path.dirname(__file__)
        try:
            # look next to module
            self.dll = ctypes.windll.LoadLibrary(os.path.join(path, library))
        except WindowsError:
            # look in current directory
            self.dll = ctypes.windll.LoadLibrary(library)

        self.dll.LFT_Connect.restype = ctypes.c_voidp

    def Connect():
        self.device = self.dll.LFT_Connect()
        if self.device is None:
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def Disconnect():
        err = self.dll.LFT_Disconnect(self.device)
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def SetMode(mode):
        err = self.dll.LFT_SetMode(self.device, ctypes.c_int(mode))
        self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def Purge():
        err = self.dll.LFT_Purge(self.device)
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def FIFOSendShorts(data):
        nSamps    = len(data)
        cDataType = ctypes.c_short * nSamps
        cData     = cDataType()
        for i in range(nSamps):
            cData[i] = data[i] 
        err = self.dll.LFT_FIFOSendShorts(self.device, data)
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def FIFOSendBytes(data):
        nSamps    = len(data)
        cDataType = ctypes.c_byte * nSamps
        cData     = cDataType()
        for i in range(nSamps):
            cData[i] = data[i] 
        err = self.dll.LFT_FIFOSendBytes(self.device, data)
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def SetReset(pinState):
        err = self.dll.LFT_FPGASetReset(self.device, ctypes.c_int(pinState))
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def FPGAWriteAddress(address):
        err = self.dll.LFT_FPGAWriteAddress(self.device, ctypes.c_int(address))
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def FPGAWriteData(data):
        err = self.dll.LFT_FPGAWriteData(self.device, ctypes.c_byte(data))
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def FPGAReadData():
        data = ctypes.c_byte()
        err = self.dll.LFT_FPGAReadData(self.device, ctypes.byref(data))
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)
        return data

    def SPISetChipSelect(pinState):
        err = self.dll.LFT_SPISetChipSelect(self.device, ctypes.c_int(pinState))
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def SPIReadByte(address):
        data = ctypes.c_byte()
        err = self.dll.LFT_SPIReadByte(self.device, ctypes.c_int(address), ctypes.byref(data))
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def SPIWriteBytes(address, data):
        nBytes = len(data)
        cDataType = ctypes.c_byte * nBytes
        cData = cDataType()
        for i in range(nBytes):
            cData[i] = data[i]
        err = self.dll.LFT_SPIWriteBytes(self.device, ctypes.c_int(address), cData)
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)

    def SPIWriteShorts(address, data):
        nBytes = len(data)
        cDataType = ctypes.c_short * nBytes
        cData = cDataType()
        for i in range(nBytes):
            cData[i] = data[i]
        err = self.dll.LFT_SPIWriteShorts(self.device, ctypes.c_int(address), cData)
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.string)


class FTSyncFifoDeviceException(Exception):
    """Exception class for FTSyncFifoDevice errors"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)