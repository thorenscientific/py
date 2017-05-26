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

        self.NoReq = 0
        self.ReqAck = 1
        self.ReqNack = 2

        self.Ack = 0
        self.Nack = 1
        
        # load the library
        library = 'FTSyncFifoDevice.dll'
        path = os.path.dirname(__file__)
        try:
            # look next to module
            self.dll = ctypes.cdll.LoadLibrary(os.path.join(path, library))
        except WindowsError:
            # look in current directory
            self.dll = ctypes.cdll.LoadLibrary(library)

        self.dll.LFT_OpenByDescription.restype = ctypes.c_voidp
        self.dll.LFT_OpenBySerialNumber.restype = ctypes.c_void_p

    def OpenByDescription(self, descriptions):
        self.device = self.dll.LFT_OpenByDescription(self.concatStrs(descriptions))
        if self.device is None:
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.value)

    def OpenBySerialNumber(self, serialNumber):
        self.device = self.dll.LFT_OpenBySerialNumber(ctypes.c_char_p(serialNumber))
        if self.device is None:
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.value)

    def throwOnErr(self, err):
        if (err != 0):
            self.dll.LFT_GetErrorInfo(self.MaxErrChars, self.errBuff)
            raise FTSyncFifoDeviceException(self.errBuff.value)

    def GetSerialNumber(self):
        buff = ctypes.create_string_buffer(32)
        self.throwOnErr(self.dll.LFT_GetSerialNumber(self.device, 32, buff))
        return buff.value

    def GetDescription(self):
        buff = ctypes.create_string_buffer(64)
        self.throwOnErr(self.dll.LFT_GetDescription(self.device, 64, buff))
        return buff.value

    def Close(self):
        self.throwOnErr(self.dll.LFT_Close(self.device))

    def SetMode(self, mode):
        self.throwOnErr(self.dll.LFT_SetMode(self.device, ctypes.c_int(mode)))

    def Purge(self):
        self.throwOnErr(self.dll.LFT_Purge(self.device))


    def FIFOSendBytes(self, data):
        nSamps    = len(data)
        cDataType = ctypes.c_ubyte * nSamps
        cData     = cDataType()
        for i in range(nSamps):
            cData[i] = data[i] 
        self.throwOnErr(self.dll.LFT_FIFOSendBytes(self.device, data))

    def FIFOSendUShorts(self, data):
        nSamps    = len(data)
        cDataType = ctypes.c_ushort * nSamps
        cData     = cDataType()
        for i in range(nSamps):
            cData[i] = data[i] 
        self.throwOnErr(self.dll.LFT_FIFOSendUShorts(self.device, nSamps, cData))

    def FIFOReceiveBytes(self, nSamps):
        cDataType = ctypes.c_ubyte * nSamps
        cData     = cDataType()
        nSampsRead = ctypes.c_int()
        self.throwOnErr(self.dll.LFT_FIFOReceiveBytes(self.device, nSamps, cData, ctypes.byref(nSampsRead)))
        return nSampsRead.value, cData

    def FIFOReceiveUShorts(self, nSamps):
        cDataType = ctypes.c_ushort * nSamps
        cData     = cDataType()
        nSampsRead = ctypes.c_int()
        self.throwOnErr(self.dll.LFT_FIFOReceiveUShorts(self.device, nSamps, cData, ctypes.byref(nSampsRead)))
        return nSampsRead.value, cData

    def FIFOReceiveUInts(self, nSamps):
        cDataType = ctypes.c_uint * nSamps
        cData     = cDataType()
        nSampsRead = ctypes.c_int()
        self.throwOnErr(self.dll.LFT_FIFOReceiveUInts(self.device, nSamps, cData, ctypes.byref(nSampsRead)))
        return nSampsRead.value, cData
    def FIFOSendBytes(self, data):
        nSamps    = len(data)
        cDataType = ctypes.c_ubyte * nSamps
        cData     = cDataType()
        for i in range(nSamps):
            cData[i] = data[i] 
        self.throwOnErr(self.dll.LFT_FIFOSendBytes(self.device, nSamps, cData))

    def SetReset(self, pinState):
        self.throwOnErr(self.dll.LFT_FPGASetReset(self.device, ctypes.c_int(pinState)))

    def FPGAWriteAddress(self, address):
        self.throwOnErr(self.dll.LFT_FPGAWriteAddress(self.device, ctypes.c_int(address)))

    def FPGAWriteData(self, data):
        self.throwOnErr(self.dll.LFT_FPGAWriteData(self.device, ctypes.c_ubyte(data)))

    def FPGAReadData(self):
        data = ctypes.c_ubyte()
        self.throwOnErr(self.dll.LFT_FPGAReadData(self.device, ctypes.byref(data)))
        return data.value

    def FPGAI2CSetAddress(self, address):
        self.throwOnErr(self.dll.LFT_FPGAI2CSetAddress(self.device, ctypes.c_int(address)))

    def FPGAI2CStart(self):
        self.throwOnErr(self.dll.LFT_FPGAI2CStart(self.device))

    def FPGAI2CStop(self):
        self.throwOnErr(self.dll.LFT_FPGAI2CStop(self.device))

    def FPGAI2CWrite(self, data, ackReq = 1):
        self.throwOnErr(self.dll.LFT_FPGAI2CWrite(self.device, ctypes.c_ubyte(data), ctypes.c_int(ackReq)))

    def FPGAI2CRead(self, ackType = 0):
        data = ctypes.c_ubyte()
        self.throwOnErr(self.dll.LFT_FPGAI2CRead(self.device, ctypes.byref(data), ctypes.c_int(ackType)))
        return data.value

    def FPGAI2CReadBytes(self, nBytes):
        cDataType = ctypes.c_ubyte * nSamps
        cData     = cDataType()
        self.throwOnErr(self.dll.LFT_FPGAI2CReadBytes(self.device, nSamps, cData));
        return cData.value

    def FPGAI2CReadString(self, nBytes):
        cData = ctypes.create_string_buffer(nBytes+1)
        self.throwOnErr(self.dll.LFT_FPGAI2CReadString(self.device, nBytes+1, cData));
        return str(cData.value)

    def SPISetChipSelect(self, pinState):
        self.throwOnErr(self.dll.LFT_SPISetChipSelect(self.device, ctypes.c_int(pinState)))

    def SPIReadByte(self, address):
        data = ctypes.c_ubyte()
        self.throwOnErr(self.dll.LFT_SPIReadByte(self.device, ctypes.c_int(address), ctypes.byref(data)))
        return data.value

    def SPIWriteByte(self, address, data):
        self.throwOnErr(self.dll.LFT_SPIWriteByte(self.device, ctypes.c_int(address), ctypes.c_ubyte(data)))

    def SPIWriteBytes(self, address, data):
        nBytes = len(data)
        cDataType = ctypes.c_ubyte * nBytes
        cData = cDataType()
        for i in range(nBytes):
            cData[i] = data[i]
        self.throwOnErr(self.dll.LFT_SPIWriteBytes(self.device, ctypes.c_int(address), cData))
        return [d.value for d in cData]

    def SPIWriteUShorts(self, address, data):
        nBytes = len(data)
        cDataType = ctypes.c_ushort * nBytes
        cData = cDataType()
        for i in range(nBytes):
            cData[i] = data[i]
        self.throwOnErr(self.dll.LFT_SPIWriteShorts(self.device, ctypes.c_int(address), cData))

    def concatStrs(self, strings):
        catStr = ""
        for string in strings:
            catStr += string + "\00"

        catStr += "\00"

        return ctypes.create_string_buffer(catStr)

class FTSyncFifoDeviceException(Exception):
    """Exception class for FTSyncFifoDevice errors"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
