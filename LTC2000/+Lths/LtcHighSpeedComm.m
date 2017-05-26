classdef LtcHighSpeedComm < handle
    % LtcHighSpeedComm Wrapper for LtcHighSpeedComm.dll
    
    properties (Access = private)
        handle;
        bufferPtr;
    end
    
    methods (Access = private)
        function errorOnBadStatus(self, id, status)
            if status ~= 0
                message = repmat(' ', 1, 256);
                [~, ~, message] = calllib('LtcHighSpeedComm', ...
                    'LthsGetErrorInfo', self.handle, message, 256);
                error(['LtcHighSpeedComm:', id],  message);
            end
        end
        
        function varargout = callWithStatus(self, func, varargin)
            [varargout{1:nargout}] = calllib('LtcHighSpeedComm', func, ...
                self.handle, varargin{:});
        end
        
        function varargout = call(self, func, varargin)
            [status, ~, varargout{1:nargout}] = ...
                self.callWithStatus(func, varargin{:});
            self.errorOnBadStatus(func, status);
        end
        
        function fixBuffer(self, type, size)
            if ~strcmp(self.bufferPtr.DataType, type) || ...
                    length(self.bufferPtr.Value) < size
               self.bufferPtr = libpointer(type, zeros(1, size)); 
            end
        end
    end
    
    methods
        function self = LtcHighSpeedComm(deviceInfo)
            if ~libisloaded('LtcHighSpeedComm')
                loadlibrary LtcHighSpeedComm.dll LtcHighSpeedCommProto
            end
            deviceStruct = struct(...
                'serial_number', uint8(zeros(1, 16)), ...
                'description', uint8(zeros(1,64)), ...
                'indices', uint8(deviceInfo.indices));
            n = length(deviceInfo.serialNumber);
            deviceStruct.serial_number(1:n) = deviceInfo.serialNumber;
            n = length(deviceInfo.description);
            deviceStruct.description(1:n) = deviceInfo.description;
            self.handle = [];
            self.bufferPtr = libpointer('uint8Ptr', 0);
            [status, self.handle] = calllib('LtcHighSpeedComm', ...
                'LthsInitDevice', self.handle, deviceStruct);
            if status ~= 0
                error('LtcHighSpeedComm:LtcHighSpeedComm', ...
                    'Error creating device');
            end
        end
        
        function delete(self)
            self.callWithStatus('LthsCleanup');
            unloadlibrary LtcHighSpeedComm
        end
        
        function description = getDescription(self)
            description = repmat(' ', 1, 64);
            description = self.call('LthsGetDescription', description, 64);
        end
        
        function serialNumber = getSerialNumber(self)
            % returns the serial number of the device
            serialNumber = repmat(' ', 1, 64);
            serialNumber = self.call('LthsGetSerialNumber', ...
                serialNumber, 64);
        end
        
        function setTimeouts(self, readTimeout, writeTimeout)
            self.call('LthsSetTimeouts', int32(readTimeout), ...
                int32(writeTimeout));
        end
        
        function setBitMode(self, bitMode)
            if bitMode == Lths.BitMode.FIFO
                self.call('LthsSetBitMode', 64);
            elseif bitMode == Lths.BitMode.MPSSE
                self.call('LthsSetBitMode', 2);
            else
                error('LtcHighSpeedComm:setBitMode', ...
                    ['bitMode must be Lths.BitMode.MPSSE or ', ...
                    'Lths.BitMode.FIFO']);
            end
        end
        
        function purgeIo(self)
            self.call('LthsPurgeIo');
        end
        
        function close(self)
            self.callWithStatus('LthsClose');
        end
        
        function nSent = fifoSendBytes(self, values)
            nSent = 0;
            [~, nSent] = self.call('LthsFifoSendBytes', ...
                values, length(values), nSent);
        end
        
        function nSent = fifoSendUint16Values(self, values)
            nSent = 0;
            [~, nSent] = self.call('LthsFifoSendUint16Values', values, ...
                length(values), nSent);
        end
        
        function nSent = fifoSendUint32Values(self, values)
            nSent = 0;
            [~, nSent] = self.call('LthsFifoSendUint32Values', values, ...
                length(values), nSent);
        end
        
        function values = fifoReceiveBytes(self, nValues)
            self.fixBuffer('uint8Ptr', nValues);
            nReceived = 0;
            values = self.call('LthsFifoReceiveBytes', self.bufferPtr, ...
                nValues, nReceived);
        end
        
        function values = fifoReceiveUint16Values(self, nValues)
            self.fixBuffer('uin16Ptr', nValues);
            nReceived = 0;
            values = self.call('LthsFifoReceiveUint16Values', ...
                self.bufferPtr, nValues, nReceived);
        end
        
        function values = fifoReceiveUint32Values(self, nValues)
            self.fixBuffer('uint32Ptr', nValues);
            nReceived = 0;
            values = self.call('LthsFifoReceiveUint32Values', ...
                self.bufferPtr, nValues, nReceived);
        end
               
        function spiSetMode(self, mode)
           if mode == Lths.SpiMode.Mode0
               spiMode = 0;
           elseif mode == Lths.SpiMode.Mode2
               spiMode = 2;
           else
               error('LtcHighSpeedComm:spiSetMode', ...
                   'mode must be Lths.SpiMode.Mode0 or Lths.SpiMode.Mode2')
           end
           self.call('LthsSpiSetMode', spiMode);
        end
        
        function spiSendBytes(self, values)
            self.call('LthsSendBytes', values, length(values));
        end
        
        function values = spiReceiveBytes(self, nValues)
            
        end
        
        function spiReceivedValues = spiTransceiveBytes(self, sendValues)
            
        end
        
        function spiSendByteAtAddress(self, address, numAddressBytes, ...
                values)
           self.call('LthsSpiSendByteAtAddress', address, ...
               numAddressBytes, values);
        end
        
        function spiSendBytesAtAddress(self, address, numAddressBytes, ...
                values)
           self.call('LthsSpiSendBytesAtAddress', address, ...
               numAddressBytes, values, length(values));
        end
        
        function values = spiReceiveByteAtAddress(self, address, ...
                numAddressBytes)
            self.fixBuffer('uint8Ptr', 1);
            values = self.call('LthsSpiReceiveByteAtAddress', address, ...
                numAddressBytes, self.bufferPtr);
        end
        
        function values = spiReceiveBytesAtAddress(self, address, ...
                numAddressBytes, nValues)
            self.fixBuffer('uint8Ptr', nValues);
            values = self.call('LthsSpiReceiveBytesAtAddress', address, ...
                numAddressBytes, self.bufferPtr, nValues);
        end
        
        function spiSetChipSelect(self, pinState)
            
        end
        
        function spiSendNoChipSelect(self, values)
            
        end
        
        function values = spiReceiveNoChipSelect(self, nValues)
            
        end
        
        function receiveValues = spiTransceiveNoChipSelect(self, ...
                sendValues)
            
        end
        
        function fpgaSetReset(self, pinState)
           if pinState == Lths.PinState.HIGH
               self.call('LthsFpgaSetReset', 1);
           elseif pinState == Lths.PinState.LOW
               self.call('LthsFpgaSetReset', 0);
           else
               error('LtcHighSpeedComm:fpgaSetReset', ...
                   ['PinState must be Lths.PinState.HIGH or ', ...
                   'Lths.PinState.LOW']);
           end
        end
        
        function fpgaWriteAddress(self, address)
            self.call('LthsFpgaWriteAddress', address);
        end
        
        function fpgaWriteData(self, data)
            self.call('LthsFpgaWriteData', data);
        end
        
        function data = fpgaReadData(self)
            data = 0;
            data = self.call('LthsFpgaReadData', data);
        end
        
        function fpgaWriteDataAtAddress(self, address, data)
            self.call('LthsFpgaWriteDataAtAddress', address, data);
        end
        
        function data = fpgaReadDataAtAddress(self, address)
            data = self.call('LthsFpgaReadDataAtAddress', address);
        end
              
        function gpioWriteHighByte(self, value)
            self.call('LthsGpioWriteHighByte', value);
        end
        
        function value = gpioReadHighByte(self)
            
        end
        
        function gpioWriteLowByte(self, value)
        
        end
        
        function value = gpioReadLowByte(self)
            
        end
        
        function fpgaI2cSetBitBangRegister(self, registerAddress)
            self.call('LthsFpgaI2cSetBitBangRegister', registerAddress);
        end
        
        function fpgaI2cSendBytes(self, address, values)
            
        end
        
        function values = fpgaI2cReceiveBytes(self, address, nValues)
            
        end
        
        function string = fpgaI2cReceiveString(self, address, nChars)
            
        end
    end
    
end

