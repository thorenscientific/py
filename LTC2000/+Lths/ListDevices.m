function deviceList = ListDevices()
% ListDevices Returns an array of structs with device information

if ~libisloaded('LtcHighSpeedComm')
    loadlibrary LtcHighSpeedComm.dll LtcHighSpeedCommProto
end

nDevices = uint32(0);
[status, nDevices] = calllib('LtcHighSpeedComm', ...
   'LthsCreateDeviceList', nDevices);
if status ~= 0
    error('LtcHighSpeedComm:ListDevices', 'Error creating device list');
end

if nDevices == 0
    error('LtcHighSpeedComm:ListDevices', 'No devices found');
end

deviceStructArray = [];
[status, deviceStructArray] = calllib('LtcHighSpeedComm', ...
    'LthsGetDeviceList', deviceStructArray, nDevices);

if status ~= 0
    error('LtcHighSpeedComm:ListDevices', 'Error getting the device list');
end

nDevices = length(deviceStructArray);
deviceCells = { cell(1, nDevices) };
deviceList = struct('serialNumber', deviceCells, ...
    'description', deviceCells, 'indices', deviceCells);
for i = 1:nDevices
    tmp = char(deviceStructArray(i).serial_number);
    deviceList(i).serialNumber = tmp(1:(find(tmp == 0, 1) - 1));
    tmp = char(deviceStructArray(i).description);
    deviceList(i).description = tmp(1:(find(tmp == 0, 1) - 1));
    deviceList(i).indices = deviceStructArray(i).indices;
end

unloadlibrary LtcHighSpeedComm

end

