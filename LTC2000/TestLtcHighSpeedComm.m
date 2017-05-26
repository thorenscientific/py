DESCRIPTIONS = {'LTC UFO BOARD', 'LTC Communication Interface', ...
    'LTC2000 Demoboard'};

foundDevice = false;
for deviceInfo = Lths.ListDevices()
   if any(strcmp(deviceInfo.description, DESCRIPTIONS))
       foundDevice = true;
       break;
   end
end

if ~foundDevice
    error('Could not find a device');
end

device = Lths.LtcHighSpeedComm(deviceInfo);
display(device.getSerialNumber());

device.setBitMode(Lths.BitMode.MPSSE);
device.gpioWriteHighByte(0);

device.delete();
