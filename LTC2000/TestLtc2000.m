clear all;

AMPLITUDE = 32000;
NUM_CYCLES = 800;
VERBOSE = true;
SLEEP_TIME = 0.1;
NUM_SAMPLES = 65536;

DESCRIPTIONS = {'LTC UFO BOARD', 'LTC Communication Interface', ...
    'LTC2000 Demoboard'};

%registers defined here
ltc2000_functions



if VERBOSE
    fprintf('LTC2000 Interface Program\n');
end

foundDevice = false;
for deviceInfo = Lths.ListDevices()
   if any(strcmp(deviceInfo.description, DESCRIPTIONS))
       foundDevice = true;
       break;
   end
end

if ~foundDevice
    error('Could not find a compatible device\n');
end

device = Lths.LtcHighSpeedComm(deviceInfo);

device.setBitMode(Lths.BitMode.MPSSE);

device.fpgaSetReset(Lths.PinState.LOW); % Issue reset pulse
device.fpgaSetReset(Lths.PinState.HIGH);

device.fpgaWriteAddress(FPGA_ID_REG);
id = device.fpgaReadData();
if VERBOSE
   fprintf('FPGA Load ID: 0x%04X\n', id);
   fprintf('Reading PLL status, should be 0x57\n');
   device.fpgaWriteAddress(FPGA_STATUS_REG);
   status = device.fpgaReadData();
   fprintf('And it is... 0x%04X\n', status);
   fprintf('Turning on DAC...\n');
end

device.fpgaWriteAddress(FPGA_DAC_PD);
device.fpgaWriteData(1);        % Turn on DAC

pause(SLEEP_TIME);

if VERBOSE
    fprintf('Configuring ADC over SPI\n');
end



spiWrite(device, REG_RESET_PD, 0);
spiWrite(device, REG_CLK_CONFIG, 2);    % setting output current to 7mA?
spiWrite(device, REG_CLK_PHASE, 7);     % DCKIP/N delay = 315 ps
spiWrite(device, REG_PORT_EN, 11);      % Enables Port A and B Rxs and allows DAC to be updated from A and B
spiWrite(device, REG_SYNC_PHASE, 0);    
spiWrite(device, REG_LINER_GAIN, 0);
spiWrite(device, REG_LINEARIZATION, 8);
spiWrite(device, REG_DAC_GAIN, 32);
spiWrite(device, REG_LVDS_MUX, 0);
spiWrite(device, REG_TEMP_SELECT, 0);
spiWrite(device, REG_PATTERN_ENABLE, 0);

pause(SLEEP_TIME);

if VERBOSE 
    % register_dump(device);
    for k = 1:9
        fprintf('Register %d: 0x%02X\n', k, spiRead(device, k));
    end
end

device.fpgaWriteAddress(FPGA_CONTROL_REG);
device.fpgaWriteData(32);

pause(SLEEP_TIME);

% Generate sine data
data = round(AMPLITUDE * sin((NUM_CYCLES * 2 * pi / NUM_SAMPLES) * ...
    (0:(NUM_SAMPLES - 1))));

sinc_data = zeros(NUM_SAMPLES, 1);
for i = 1:NUM_SAMPLES
x = ((i - 32768) / (512.0)) + 0.0001;
sinc_data(i) = int16((32000 * (sin(x) / x)));
end


% Testing file I/O
fprintf('writing data out to file')
outfile = fopen('dacdata_sinc.csv', 'w');
for i = 1 : NUM_SAMPLES
    fprintf(outfile, '%d\n', sinc_data(i));
end
fclose(outfile);
fprintf('\ndone writing!')

indata = zeros(NUM_SAMPLES, 1);

fprintf('\nreading data from file')
infile = fopen('dacdata_sinc.csv', 'r');
for i = 1: NUM_SAMPLES 
    indata(i) = str2double(fgetl(infile));
end
fclose(infile);
fprintf('\ndone reading!')
    
device.setBitMode(Lths.BitMode.FIFO);
numBytesSent = device.fifoSendUint16Values(indata);
fprintf('\nnumBytesSent (should be %d) = %d\n', NUM_SAMPLES * 2, ...
    numBytesSent);

delete(device);