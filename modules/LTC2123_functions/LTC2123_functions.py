import FTSyncFifoDevicePy
from time import sleep

sleeptime = 0.1
swapbytes = 1 # Swap bytes until read function is changed...

# FPGA register addresses
ID_REG = 0x00
CAPTURE_CONFIG_REG = 0x01
CAPTURE_CONTROL_REG = 0x02
CAPTURE_RESET_REG = 0x03
CAPTURE_STATUS_REG = 0x04
SPI_CONFIG_REG = 0x05
CLOCK_STATUS_REG = 0x06
JESD204B_WB0_REG = 0x07
JESD204B_WB1_REG = 0x08
JESD204B_WB2_REG = 0x09
JESD204B_WB3_REG = 0x0A
JESD204B_CONFIG_REG = 0x0B
JESD204B_RB0_REG = 0x0C
JESD204B_RB1_REG = 0x0D
JESD204B_RB2_REG = 0x0E
JESD204B_RB3_REG = 0x0F
JESD204B_CHECK_REG = 0x10

MOD_RPAT = [0xBE, 0xD7, 0x23, 0x47, 0x6B, 0x8F, 0xB3, 0x14, 0x5E, 0xFB, 0x35, 0x59]

class NumSamp:
    def __init__(self, memSize, buffSize):
        self.MemSize = memSize
        self.BuffSize = buffSize
    
NumSamp128  = NumSamp(0x00, 128)
NumSamp256  = NumSamp(0x10, 256)
NumSamp512  = NumSamp(0x20, 512)
NumSamp1K   = NumSamp(0x30, 1024)
NumSamp2K   = NumSamp(0x40, 2 * 1024)
NumSamp4K   = NumSamp(0x50, 4 * 1024)
NumSamp8K   = NumSamp(0x60, 8 * 1024)
NumSamp16K  = NumSamp(0x70, 16 * 1024)
NumSamp32K  = NumSamp(0x80, 32 * 1024)
NumSamp64K  = NumSamp(0x90, 64 * 1024)
NumSamp128K = NumSamp(0xA0, 128 * 1024)

#def read_reg(address)

#def write_reg(address, data)

def write_jesd204b_reg(device, address, b3, b2, b1, b0):
#    device.Connect()
    device.SetMode(device.ModeMPSSE)

    device.FPGAWriteAddress(JESD204B_WB3_REG)
    device.FPGAWriteData(b3)
    device.FPGAWriteAddress(JESD204B_WB2_REG)
    device.FPGAWriteData(b2)
    device.FPGAWriteAddress(JESD204B_WB1_REG)
    device.FPGAWriteData(b1)
    device.FPGAWriteAddress(JESD204B_WB0_REG)
    device.FPGAWriteData(b0)
    device.FPGAWriteAddress(JESD204B_CONFIG_REG)
    device.FPGAWriteData((address << 2) | 0x02)
    #sleep(0.1)
    status = device.FPGAReadData()
#    device.Disconnect()
    if((status & 0x01) == 0):
        print "Error writing JESD204B register"

def read_jesd204b_reg(device, address):
#    device.Connect()
    device.SetMode(device.ModeMPSSE)
    
    device.FPGAWriteAddress(JESD204B_CHECK_REG) # Write address of JESD204B Check Register
    device.FPGAWriteData(address<<2 | 0x02)
    #sleep(0.1)
    status = device.FPGAReadData()
    if((status & 0x01) == 0):
        print "Error Reading JESD204B register"
    device.FPGAWriteAddress(JESD204B_RB3_REG)
    b3 = device.FPGAReadData()
    device.FPGAWriteAddress(JESD204B_RB2_REG)
    b2 = device.FPGAReadData()
    device.FPGAWriteAddress(JESD204B_RB1_REG)
    b1 = device.FPGAReadData()
    device.FPGAWriteAddress(JESD204B_RB0_REG)
    b0 = device.FPGAReadData()
#    device.Disconnect()
    return b3, b2, b1, b0

    
def hexStr(data):
    return '0x' + '{:04X}'.format(data)


    
def next_pbrs(data):
    next_pbrs = ((data << 1) ^ (data << 2)) & 0b1111111111111100
    next_pbrs |= (((next_pbrs >> 15) ^ (next_pbrs >> 14)) & 0x0001)    # find bit 0
    next_pbrs |= (((next_pbrs >> 14) ^ (data << 1)) & 0x0002)    # find bit 1
    return next_pbrs

     
def dump_ADC_registers(device):
    device.SetMode(device.ModeMPSSE)
    print "LTC2124 Register Dump: " 
    print "Register 1: 0x{:02X}".format(device.SPIReadByte(0x81))
    print "Register 2: 0x{:02X}".format(device.SPIReadByte(0x82))
    print "Register 3: 0x{:02X}".format(device.SPIReadByte(0x83))
    print "Register 4: 0x{:02X}".format(device.SPIReadByte(0x84))
    print "Register 5: 0x{:02X}".format(device.SPIReadByte(0x85))
    print "Register 6: 0x{:02X}".format(device.SPIReadByte(0x86))
    print "Register 7: 0x{:02X}".format(device.SPIReadByte(0x87))
    print "Register 8: 0x{:02X}".format(device.SPIReadByte(0x88))
    print "Register 9: 0x{:02X}".format(device.SPIReadByte(0x89))
    print "Register A: 0x{:02X}".format(device.SPIReadByte(0x8A))   
    
def open_UFO_and_reset(res):
    device = FTSyncFifoDevicePy.FTSyncFifoDevice()
    device.OpenByDescription(['LTC UFO Board', 'LTC Communication Interface'])
    serial = device.GetSerialNumber()
    device.SetMode(device.ModeMPSSE)
    if(res == 1):
        device.SetReset(device.PinStateLow) #Issue reset pulse
        device.SetReset(device.PinStateHigh)
    return device


def capture4(device, n, lanes, dumpdata, dump_pscope_data, verbose):
# Configuration Flow Step 11: Reset Capture Engine
#    device.SetMode(device.ModeMPSSE)
#    device.FPGAWriteAddress(CAPTURE_RESET_REG) 
#    device.FPGAWriteData(0x01)  #Reset
# Step 24
    device.FPGAWriteAddress(CLOCK_STATUS_REG)
    clockstat = device.FPGAReadData()
    if(verbose != 0):
        print "Reading Clock Status register; should be 0x16 (or at least 0x04 bit set)"
        print "Register 6   (Clock status): 0x{:04X}".format(clockstat)
# Step 25
    device.FPGAWriteAddress(CAPTURE_STATUS_REG)
    capturestat = device.FPGAReadData()
    syncErr = (capturestat & 0x04) != 0
    if (verbose != 0):
        print "Reading capture status, should be 0xF0 (CH0, CH1, CH2, CH3 valid, Capture NOT done, data not fetched)"
        print "And it is... 0x{:04X}".format(capturestat)
# Step 26 in config flow
    device.FPGAWriteAddress(CAPTURE_CONFIG_REG)
    device.FPGAWriteData(n.MemSize | 0x08) # CH0 and CH1
# Step 27
    device.FPGAWriteAddress(CAPTURE_CONTROL_REG)
    device.FPGAWriteData(0x00)  #Set FETONLY low first
    device.FPGAWriteData(0x01)  #Start!! With FETONLY as 0
    sleep(1) #wait for capture
# Step 28
    device.FPGAWriteAddress(CAPTURE_STATUS_REG)
    capturestat = device.FPGAReadData()
    syncErr = (capturestat & 0x04) != 0
    if (verbose != 0):
        print "Reading capture status, should be 0xF1 (CH0, CH1, CH2, CH3 valid, Capture  IS done, data not fetched)"
        print "And it is... 0x{:04X}".format(capturestat)
# Step 29
    device.SetMode(device.ModeFIFO)
    sleep(0.1)
# Step 30
    nSampsRead, data01 = device.FIFOReceiveUShorts(n.BuffSize + 100)#/2) #/4??
    if(verbose != 0):
        print "Read out " + str(nSampsRead) + " samples for CH0, 1"

# Okay, now get CH2, CH3 data...
# Step 31 
    device.SetMode(device.ModeMPSSE)
# Step 32
    device.FPGAWriteAddress(CAPTURE_RESET_REG) 
    device.FPGAWriteData(0x01)  #Reset
# Step 33
    device.FPGAWriteAddress(CAPTURE_CONFIG_REG)
    device.FPGAWriteData(n.MemSize | 0x0A) # CH2 and CH3
# Step 34
    device.FPGAWriteAddress(CAPTURE_CONTROL_REG)
    device.FPGAWriteData(0x02)  # Set FETONLY high FIRST!!
    device.FPGAWriteData(0x03)  #Start!! With FETONLY as 1
    sleep(1) #wait for capture
# Step 35
    device.FPGAWriteAddress(CAPTURE_STATUS_REG)
    capturestat = device.FPGAReadData()
    syncErr = (capturestat & 0x04) != 0
    if (verbose != 0):
        print "Reading capture status, should be 0xF1 (CH0, CH1, CH2, CH3 valid, Capture  IS done, data not fetched)"
        print "And it is... 0x{:04X}".format(capturestat)
# Step 36
    device.SetMode(device.ModeFIFO)
    sleep(0.1)
# Step 37
    nSampsRead, data23 = device.FIFOReceiveUShorts(n.BuffSize + 100)#/2)
    if(verbose != 0):
        print "Read out " + str(nSampsRead) + " samples for CH2, 3"

    #Fix byte alignment...
    if(swapbytes != 0):
        for i in range(0, nSampsRead):
            data01[i] = (((data01[i] & 0xFF00)>>8) | ((data01[i] & 0x00FF)<<8)) & 0x0000FFFF
            data23[i] = (((data23[i] & 0xFF00)>>8) | ((data23[i] & 0x00FF)<<8)) & 0x0000FFFF
    else:
        for i in range(0, nSampsRead):
            data01[i] = data01[i] & 0x0000FFFF
            data23[i] = data23[i] & 0x0000FFFF


    # Initialize data arrays
    data_ch0 = [0]*(nSampsRead/2)
    data_ch1 = [0]*(nSampsRead/2)
    data_ch2 = [0]*(nSampsRead/2)
    data_ch3 = [0]*(nSampsRead/2)



    for i in range(0, (nSampsRead)/4):
# Split data for CH0, CH1
        data_ch0[i*2] = data01[i*4]
        data_ch0[i*2+1] = data01[i*4+1]
        data_ch1[i*2] = data01[i*4+2]
        data_ch1[i*2+1] = data01[i*4+3]
# Split data for CH2, CH3
        data_ch2[i*2] = data23[i*4]
        data_ch2[i*2+1] = data23[i*4+1]
        data_ch3[i*2] = data23[i*4+2]
        data_ch3[i*2+1] = data23[i*4+3]


    if(dumpdata !=0):
        for i in range(0, min(dumpdata, nSampsRead/2)):
                print '0x' + '{:04X}'.format(data_ch0[i]) + ', 0x' + '{:04X}'.format(data_ch1[i])+ ', 0x' + '{:04X}'.format(data_ch2[i])+ ', 0x' + '{:04X}'.format(data_ch3[i])

# This section was added for debugging the raw data from the FIFO. Consider
# making a "dumpraw" option...
#    print ('dumping raw data from readUShorts')
#    for i in range(0, nSampsRead):
#        print '0x' + '{:04X}'.format(data01[i]) + ', 0x' + '{:04X}'.format(data23[i])

    nSamps_per_channel = nSampsRead/2
    return data_ch0, data_ch1, data_ch2, data_ch3, nSamps_per_channel, syncErr




def pattern_checker(data, nSamps_per_channel, dumppattern):
    printError = True
    errorcount = nSamps_per_channel - 1 #Start big
    #periodicity = lastperiodicity = 0
    golden = next_pbrs(data[0])
    for i in range(0, nSamps_per_channel-1):
        next = next_pbrs(data[i])
        if(i<dumppattern):
            print 'data: 0x' + '{:04X}'.format(data[i]) + ', next: 0x' +'{:04X}'.format(next) + ', XOR: 0x' +'{:04X}'.format(data[i+1] ^ next) + ', golden: 0x' +'{:04X}'.format(golden)      # UN-commet for hex
            #print '0b' + '{:016b}'.format(data[i]) + ',  0x' +'{:016b}'.format(next) + ',  0x' +'{:016b}'.format(data[i] ^ next)   # UN-comment for binary
        if(data[i+1] == next):
            errorcount -= 1
        elif printError:
            printError = False
            print
            print hexStr(data[i-1]) + "; " + hexStr(data[i]) + "; " + hexStr(data[i+1])
            print
#                print "error count = " + str(errorcount)
#                device.Close() #End of main loop.
#                raise Exception("BAD DATA!!!")
        if(data[i] == data[0]):
            #periodicity = i - lastperiodicity
            lastperiodicity = i
        golden = next_pbrs(golden)


    #print "periodicity (only valid for captures > 64k): " + str(periodicity)
    #if errorcount < 0:
    #    errorcount = 100000000
    return errorcount
    
def initialize_DC2226_clocks(device, K, verbose):
    if(verbose != 0):
        print "Configuring clock generators over SPI:"
    device.SetMode(device.ModeMPSSE)

    print "Configuring LTC6950 (REFCLK generator)"
#LTC6950 config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x02)

    device.SPIWriteByte(0x00 << 1, 0x0B) # Dumb values to div by 4
    device.SPIWriteByte(0x01 << 1, 0x04) # (1200MHz in, 320MHz out)
    device.SPIWriteByte(0x02 << 1, 0x3B) # NO EZSync!!
    device.SPIWriteByte(0x03 << 1, 0x00) #
    device.SPIWriteByte(0x04 << 1, 0x00) #
    device.SPIWriteByte(0x05 << 1, 0x9B) #
    device.SPIWriteByte(0x06 << 1, 0xE0) #
    device.SPIWriteByte(0x07 << 1, 0x00) #
    device.SPIWriteByte(0x08 << 1, 0x01) #
    device.SPIWriteByte(0x09 << 1, 0x00) #
    device.SPIWriteByte(0x0A << 1, 0X32) #
    device.SPIWriteByte(0x0B << 1, 0x01) #
    device.SPIWriteByte(0x0C << 1, 0x80) #
    device.SPIWriteByte(0x0D << 1, 0x84) # ADC 2 Clock Divider
    device.SPIWriteByte(0x0E << 1, 0x80) #
    device.SPIWriteByte(0x0F << 1, 0x84) # ADC 1 Clock Divider
    device.SPIWriteByte(0x10 << 1, 0x80) #-
    device.SPIWriteByte(0x11 << 1, 0x84) # SYSREF gen divider
    device.SPIWriteByte(0x12 << 1, 0x80) #
#        device.SPIWriteByte(0x13 << 1, 0x84) #
    device.SPIWriteByte(0x13 << 1, 0x84) #
    device.SPIWriteByte(0x14 << 1, 0x80) #
    device.SPIWriteByte(0x15 << 1, 0x04) #
    device.SPIWriteByte(0x16 << 1, 0x45) #

    print "Configuring LTC6950 (REFCLK generator)"
#LTC6954 config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x03)

    device.SPIWriteByte(0x00 << 1, 0x00) # Dumb values to div by 32,
  #  device.SPIWriteByte(0x01 << 1, 0xC0) # NO EZSync!!!
    device.SPIWriteByte(0x01 << 1, 0xC0) # ADC 1 Delay SYSREF, just on this one!
    device.SPIWriteByte(0x02 << 1, K) # ADC 1 divider
    device.SPIWriteByte(0x03 << 1, 0xC0) # FPGA delay
    device.SPIWriteByte(0x04 << 1, K) # FPGA divider
    device.SPIWriteByte(0x05 << 1, 0xC5) # ADC 2 delay
    device.SPIWriteByte(0x06 << 1, K) # ADC 2 divider
    device.SPIWriteByte(0x07 << 1, 0x20) #

    sleep(sleeptime)
    device.FPGAWriteAddress(SPI_CONFIG_REG) #Assert EZsync
    device.FPGAWriteData(0x18)
    sleep(sleeptime)
    device.FPGAWriteData(0x00)
    sleep(sleeptime)
    
    
def load_ltc212x(device, cs_control=0, verbose=0, did=0xEF, bid=0x00, K=10, modes=0x00, pattern=0x00):
    if(verbose != 0):
        print "Configuring ADCs over SPI:"
    device.SetMode(device.ModeMPSSE)
#ADC config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(cs_control)

#    device.SPIWriteByte(0x00, 0x01) # reset dut
    device.SPIWriteByte(0x03, did) #Device ID to 0xAB
    device.SPIWriteByte(0x04, bid) #Bank ID to 0x01
    device.SPIWriteByte(0x05, 0x01) #2 lane mode (default)
#    device.SPIWriteByte(0x06, 0x1F) #9 frames / multiframe (0x08)
    device.SPIWriteByte(0x06, K-1)
    device.SPIWriteByte(0x07, modes) #Enable FAM, LAM
    #device.SPIWriteByte(0x07, 0x18) #Disable FAM, LAM (only needed for prerelease silicon)
    device.SPIWriteByte(0x08, 0x01) #Subclass mode
    device.SPIWriteByte(0x09, pattern) #PRBS test pattern
    device.SPIWriteByte(0x0A, 0x03) # 0x03 = 16mA CML current
    if(verbose != 0):
        print "ADC " + str(cs_control) + " configuration:"
        dump_ADC_registers(device)
        
        
def capture(device, n, channels, lanes, dumpdata, dump_pscope_data, verbose):
    device.SetMode(device.ModeMPSSE)
    device.FPGAWriteAddress(CAPTURE_CONFIG_REG)
    dec = 0

    if(channels == 1):
        device.FPGAWriteData(n.MemSize | 0x00) # Channel A active
    elif(channels == 2):
        device.FPGAWriteData(n.MemSize | 0x02) # Channel B active
    else: # Must be 3, all channels
        device.FPGAWriteData(n.MemSize | 0x08) # Both Channels active

    device.FPGAWriteAddress(CAPTURE_RESET_REG)
    device.FPGAWriteData(0x01)  #Reset

    device.FPGAWriteAddress(CAPTURE_CONTROL_REG)
    device.FPGAWriteData(0x01)  #Start!!
    sleep(1) #wait for capture

    if(verbose != 0):
        print "Reading capture status, should be 0x31 (CH0, CH1 valid, Capture done, data not fetched)"
        
    device.FPGAWriteAddress(CAPTURE_STATUS_REG)
    data = device.FPGAReadData()
    syncErr = (data & 0x04) != 0
    
    if (verbose != 0):
        print "And it is... 0x{:04X}".format(data)
        
    #sleep(sleeptime)

    device.SetMode(device.ModeFIFO)
    sleep(0.1)
    nSampsRead, data = device.FIFOReceiveUShorts(n.BuffSize)

    sleep(sleeptime)

    #if(verbose != 0):
    print "Read out " + str(nSampsRead) + " samples"

    #Fix byte alignment...
    if(swapbytes != 0):
        for i in range(0, nSampsRead):
            data[i] = (((data[i] & 0xFF00)>>8) | ((data[i] & 0x00FF)<<8)) & 0x0000FFFF
    else:
        for i in range(0, nSampsRead):
            data[i] = data[i] & 0x0000FFFF
            
    # Split CH0, CH1
    data_ch0 = data[:]
    data_ch1 = data[:]

    if(lanes == 1): #EXPERIMENT!!!
        for i in range(0, (nSampsRead)/4):
            data[i*4+0] = data_ch0[i*4+0] # This makes the PRBS work out
            data[i*4+1] = data_ch0[i*4+2]
            data[i*4+2] = data_ch0[i*4+1]
            data[i*4+3] = data_ch0[i*4+3]

    if((channels == 3) & (lanes == 2)): #Split data for 2 channel
        for i in range(0, (nSampsRead)/4):
            data_ch0[i*2] = data[i*4]
            data_ch0[i*2+1] = data[i*4+1]
            data_ch1[i*2] = data[i*4+2]
            data_ch1[i*2+1] = data[i*4+3]

    if((channels == 3) & (lanes == 1)): #Split data for 2 channel
        for i in range(0, (nSampsRead)/4):
            data_ch0[i*2] = data[i*4]
            data_ch1[i*2] = data[i*4+1]
            data_ch0[i*2+1] = data[i*4+2]
            data_ch1[i*2+1] = data[i*4+3]
     

    if(channels != 3): #One channel only
    #if(1==1): # Force print single array
        if(dumpdata !=0):
            for i in range(0, min(dumpdata, nSampsRead)):
                if(hex == 1 & dec == 1):
                    print '0x' + '{:04X}'.format(data[i]) + ', ' + str(data[i])     # UN-comment for hex
                    ##print '0x' + '{:016b}'.format(data[i]) + ', ' + str(data[i])   # UN-comment for binary
                elif(hex == 1):
                    print '0x' + '{:04X}'.format(data[i])
                elif(dec == 1):
                    print data[i]

    else: #Two channels

        if(dumpdata !=0):
            for i in range(0, min(dumpdata, nSampsRead/2)):
                if(hex == 1 & dec == 1):
                    print '0x' + '{:04X}'.format(data[2*i]) + ', ' + str(data[2*i]) + ', 0x' + '{:04X}'.format(data[2*i+1]) + ', ' + str(data[2*i+1])     # UN-comment for hex
                    #print '0b' + '{:016b}'.format(data[i]) + ', ' + str(data[i])   # UN-comment for binary
                elif(hex == 1):
                    print '0x' + '{:04X}'.format(data_ch0[i]) + ', 0x' + '{:04X}'.format(data_ch1[i])
                elif(dec == 1):
                    print str(data[2*i]) + ", " + str(data[2*i+1])

    if(dump_pscope_data != 0):
        outfile = open("pscope_data.csv", "w")
        if(channels != 3):
            for i in range(0, nSampsRead):
                outfile.write("{:d}, ,0\n".format((data[i]-32768)/4))
        else:
            for i in range(0, nSampsRead/2):
                outfile.write("{:d}, ,{:d}\n".format((data_ch0[i]-32768)/4, (data_ch1[i]-32768)/4))

        outfile.write("End\n")
        outfile.close()

    if(channels != 3): #One channel only
        nSamps_per_channel = nSampsRead
    else:               #Two channels
        nSamps_per_channel = nSampsRead/2
    return data, data_ch0, data_ch1, nSamps_per_channel, syncErr
    

def initialize_DC2226_version2_clocks_250(device, K, verbose):
    if(verbose != 0):
        print "Configuring clock generators over SPI:"
    device.SetMode(device.ModeMPSSE)

	#LTC6954 config
    print "Configuring LTC6954 (REF distribution)"
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x04) ## VERIFIED!! ##

    device.SPIWriteByte(0x00 << 1, 0x00)
    device.SPIWriteByte(0x01 << 1, 0x80) # 6951-1 delay
    device.SPIWriteByte(0x02 << 1, 0x01) # 6951-1 divider
    device.SPIWriteByte(0x03 << 1, 0x80) # 6951-2 delay
    device.SPIWriteByte(0x04 << 1, 0x01) # 6951-2 divider
    device.SPIWriteByte(0x05 << 1, 0xC0) # sync delay & CMSINV
    device.SPIWriteByte(0x06 << 1, 0x01) # sync divider
    device.SPIWriteByte(0x07 << 1, 0x21) #
    print "Configuring U10 (LTC6951) cp"
#LTC6951config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x02) ## VERIFIED!! ##
    device.SPIWriteByte(0x00 << 1, 0x05) #
    device.SPIWriteByte(0x01 << 1, 0xBA) #
    device.SPIWriteByte(0x02 << 1, 0x00) #
    device.SPIWriteByte(0x03 << 1, 0x7C) #
    device.SPIWriteByte(0x04 << 1, 0xA3) #
    device.SPIWriteByte(0x05 << 1, 0x08) #
    device.SPIWriteByte(0x06 << 1, 0x05) # 5 for 200, 6 for 300
    device.SPIWriteByte(0x07 << 1, 0x07) #
    device.SPIWriteByte(0x08 << 1, 0x01) #
    device.SPIWriteByte(0x09 << 1, 0x13) #
    device.SPIWriteByte(0x0A << 1, 0xC0) #
    device.SPIWriteByte(0x0B << 1, 0x9B) #
    device.SPIWriteByte(0x0C << 1, 0x16) # 16 for 250, 1E f0r 300
    device.SPIWriteByte(0x0D << 1, 0x93) #
    device.SPIWriteByte(0x0E << 1, 0x16) # 16 for 250, 1E for 300
    device.SPIWriteByte(0x0F << 1, 0x93) #
    device.SPIWriteByte(0x10 << 1, 0x16) # 16 for 250, 1E for 300
    device.SPIWriteByte(0x11 << 1, 0x30) #
    device.SPIWriteByte(0x12 << 1, 0x00) #
    device.SPIWriteByte(0x13 << 1, 0x11) #
    device.SPIWriteByte(0x02 << 1, 0x01) # calibrate after writing all registers
	
    print "Configuring U13 (LTC6951) cp"
#LTC6951config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x03) ## VERIFIED!! ##

    device.SPIWriteByte(0x00 << 1, 0x05) #
    device.SPIWriteByte(0x01 << 1, 0xBA) #
    device.SPIWriteByte(0x02 << 1, 0x00) #
    device.SPIWriteByte(0x03 << 1, 0x7C) #
    device.SPIWriteByte(0x04 << 1, 0xA3) #
    device.SPIWriteByte(0x05 << 1, 0x08) #
    device.SPIWriteByte(0x06 << 1, 0x05) # 5 for 250, 6 for 300
    device.SPIWriteByte(0x07 << 1, 0x07) #
    device.SPIWriteByte(0x08 << 1, 0x01) #
    device.SPIWriteByte(0x09 << 1, 0x13) #
    device.SPIWriteByte(0x0A << 1, 0xC0) #
    device.SPIWriteByte(0x0B << 1, 0x9B) #
    device.SPIWriteByte(0x0C << 1, 0x16) # 16 for 250, 1E f0r 300
    device.SPIWriteByte(0x0D << 1, 0x93) #
    device.SPIWriteByte(0x0E << 1, 0x16) # 16 for 250, 1E for 300
    device.SPIWriteByte(0x0F << 1, 0x9B) #
    device.SPIWriteByte(0x10 << 1, 0x16) # 16 for 250, 1E for 300
    device.SPIWriteByte(0x11 << 1, 0x30) #
    device.SPIWriteByte(0x12 << 1, 0x00) #
    device.SPIWriteByte(0x13 << 1, 0x11) #
    device.SPIWriteByte(0x02 << 1, 0x01) # calibrate after writing all registers
    

    print "toggle SYNC cp"
    sleep(sleeptime)
    device.FPGAWriteAddress(SPI_CONFIG_REG) #Assert EZsync
    print "sync high"
    device.FPGAWriteData(0x08)  # only toggle LTC6951 sync (LTC6954 does not need a sync with DIV=1)
    sleep(sleeptime)
    print "sync low"
    device.FPGAWriteData(0x00)
    sleep(sleeptime)


def initialize_DC2226_version2_clocks_300(device, K, verbose):
    if(verbose != 0):
        print "Configuring clock generators over SPI:"
    device.SetMode(device.ModeMPSSE)

	#LTC6954 config
    print "Configuring LTC6954 (REF distribution)"
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x04) ## VERIFIED!! ##

    device.SPIWriteByte(0x00 << 1, 0x00)
    device.SPIWriteByte(0x01 << 1, 0x80) # 6951-1 delay
    device.SPIWriteByte(0x02 << 1, 0x01) # 6951-1 divider
    device.SPIWriteByte(0x03 << 1, 0x80) # 6951-2 delay
    device.SPIWriteByte(0x04 << 1, 0x01) # 6951-2 divider
    device.SPIWriteByte(0x05 << 1, 0x80) # sync delay & CMSINV
    device.SPIWriteByte(0x06 << 1, 0x01) # sync divider
    device.SPIWriteByte(0x07 << 1, 0x21) #
    print "Configuring U10 (LTC6951) cp"
#LTC6951config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x02) ## VERIFIED!! ##
    device.SPIWriteByte(0x00 << 1, 0x05) #
    device.SPIWriteByte(0x01 << 1, 0xBA) #
    device.SPIWriteByte(0x02 << 1, 0x00) #
    device.SPIWriteByte(0x03 << 1, 0x74) #
    device.SPIWriteByte(0x04 << 1, 0xA3) #
    device.SPIWriteByte(0x05 << 1, 0x08) # RDIV, NDIV[9:8]
    device.SPIWriteByte(0x06 << 1, 0x06) # RDIV
    device.SPIWriteByte(0x07 << 1, 0x07) #
    device.SPIWriteByte(0x08 << 1, 0x01) # out0: muted
    device.SPIWriteByte(0x09 << 1, 0x13) # out0: 300MHz
    device.SPIWriteByte(0x0A << 1, 0xC0) #
    device.SPIWriteByte(0x0B << 1, 0x9B) # out1: 18.75M (sysref2)
    device.SPIWriteByte(0x0C << 1, 0x23) # delay out1: 23 for 300
    device.SPIWriteByte(0x0D << 1, 0x93) # out2: 300M (FPGA clock)
    device.SPIWriteByte(0x0E << 1, 0x1E) # delay out2: 1E for 300
    device.SPIWriteByte(0x0F << 1, 0x93) # out3: 300M (adc clock2)
    device.SPIWriteByte(0x10 << 1, 0x1E) # delay out3: 1E for 3000
    device.SPIWriteByte(0x11 << 1, 0x30) # out4: div and out powered down (0x30)
    device.SPIWriteByte(0x12 << 1, 0x00) #
    device.SPIWriteByte(0x13 << 1, 0x11) #
    device.SPIWriteByte(0x02 << 1, 0x01) # calibrate after writing all registers
	
    print "Configuring U13 (LTC6951) cp"
#LTC6951config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x03) ## VERIFIED!! ##

    device.SPIWriteByte(0x00 << 1, 0x05) #
    device.SPIWriteByte(0x01 << 1, 0xBA) #
    device.SPIWriteByte(0x02 << 1, 0x00) #
    device.SPIWriteByte(0x03 << 1, 0x74) #
    device.SPIWriteByte(0x04 << 1, 0xA3) #
    device.SPIWriteByte(0x05 << 1, 0x08) # RDIV, NDIV[9:8]
    device.SPIWriteByte(0x06 << 1, 0x06) # RDIV
    device.SPIWriteByte(0x07 << 1, 0x07) #
    device.SPIWriteByte(0x08 << 1, 0x01) # out0: muted
    device.SPIWriteByte(0x09 << 1, 0x13) # out0: 300MHz
    device.SPIWriteByte(0x0A << 1, 0xC0) #
    device.SPIWriteByte(0x0B << 1, 0x9B) # out1: 18.75M (FPGA SYSREF)
    device.SPIWriteByte(0x0C << 1, 0x23) # delay out1: 23 for 300
    device.SPIWriteByte(0x0D << 1, 0x93) # out2: 300M (ADC clock 1)
    device.SPIWriteByte(0x0E << 1, 0x1E) # delay out2: 1E for 300
    device.SPIWriteByte(0x0F << 1, 0x9B) # out3: 18.75M (adc sysref_1)
    device.SPIWriteByte(0x10 << 1, 0x23) # delay out3: 23 for 300
    device.SPIWriteByte(0x11 << 1, 0x30) # out4: div and out powered down (0x30)
    device.SPIWriteByte(0x12 << 1, 0x00) #
    device.SPIWriteByte(0x13 << 1, 0x11) #
    device.SPIWriteByte(0x02 << 1, 0x01) # calibrate after writing all registers
    

    print "toggle SYNC cp"
    sleep(sleeptime)
    device.FPGAWriteAddress(SPI_CONFIG_REG) #Assert EZsync
    print "sync high"
    device.FPGAWriteData(0x08)  # only toggle LTC6951 sync (LTC6954 does not need a sync with DIV=1)
    sleep(sleeptime)
    print "sync low"
    device.FPGAWriteData(0x00)
    sleep(sleeptime)
	
	
# After the LTC6951's are SYNC'd the CMOS outputs of the LTC6954 can be powered down 
# Powering down the LTC6954 CMOS output, sets them to a static level (low or high)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x04) ## VERIFIED!! ##
    device.SPIWriteByte(0x00 << 1, 0x10)  # power down LTC6954 output2 


def initialize_DC2226_version2_clocks_300_debug(device, K, verbose,runs):
    if(verbose != 0):
        print "Configuring clock generators over SPI:"
    device.SetMode(device.ModeMPSSE)

    clk_delay = 0x1E + runs -1  #this varies the 6951 clkout delays
    sysref_delay = 0x23 +runs-1 #this varies the 6951 sysref delays
	#LTC6954 config
    print "Configuring LTC6954 (REF distribution)"
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x04) ## VERIFIED!! ##

    device.SPIWriteByte(0x00 << 1, 0x00)
    device.SPIWriteByte(0x01 << 1, 0x80) # 6951-1 delay
    device.SPIWriteByte(0x02 << 1, 0x01) # 6951-1 divider
    device.SPIWriteByte(0x03 << 1, 0x80) # 6951-2 delay
    device.SPIWriteByte(0x04 << 1, 0x01) # 6951-2 divider
    device.SPIWriteByte(0x05 << 1, 0x80) # sync delay & CMSINV
    device.SPIWriteByte(0x06 << 1, 0x01) # sync divider
    device.SPIWriteByte(0x07 << 1, 0x21) #
    print "Configuring U10 (LTC6951) cp"
#LTC6951config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x02) ## VERIFIED!! ##
    device.SPIWriteByte(0x00 << 1, 0x05) #
    device.SPIWriteByte(0x01 << 1, 0xBA) #
    device.SPIWriteByte(0x02 << 1, 0x00) #
    device.SPIWriteByte(0x03 << 1, 0x75) #
    device.SPIWriteByte(0x04 << 1, 0xA3) #
    device.SPIWriteByte(0x05 << 1, 0x08) # RDIV, NDIV[9:8] (RDIV =2 --> 0x08, RDIV=3-->0x0C, RDIV=6 --> 0x18)
    device.SPIWriteByte(0x06 << 1, 0x06) # RDIV
    device.SPIWriteByte(0x07 << 1, 0x07) #
    device.SPIWriteByte(0x08 << 1, 0x01) # out0: muted
    device.SPIWriteByte(0x09 << 1, 0x13) # out0: 300MHz
    device.SPIWriteByte(0x0A << 1, 0xC0) #
    device.SPIWriteByte(0x0B << 1, 0x9B) # out1: 18.75M (sysref2)
    device.SPIWriteByte(0x0C << 1, sysref_delay) # delay out1: 23 for 300
    device.SPIWriteByte(0x0D << 1, 0x93) # out2: 300M (FPGA clock)
    device.SPIWriteByte(0x0E << 1, clk_delay) # delay out2: 1E for 300
    device.SPIWriteByte(0x0F << 1, 0x93) # out3: 300M (adc clock2)
    device.SPIWriteByte(0x10 << 1, clk_delay) # delay out3: 1E for 3000
    device.SPIWriteByte(0x11 << 1, 0x30) # out4: div and out powered down (0x30)
    device.SPIWriteByte(0x12 << 1, 0x00) #
    device.SPIWriteByte(0x13 << 1, 0x11) #
    device.SPIWriteByte(0x02 << 1, 0x01) # calibrate after writing all registers
	
    print "Configuring U13 (LTC6951) cp"
#LTC6951config
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x03) ## VERIFIED!! ##

    device.SPIWriteByte(0x00 << 1, 0x05) #
    device.SPIWriteByte(0x01 << 1, 0xBA) #
    device.SPIWriteByte(0x02 << 1, 0x00) #
    device.SPIWriteByte(0x03 << 1, 0x75) #
    device.SPIWriteByte(0x04 << 1, 0xA3) #
    device.SPIWriteByte(0x05 << 1, 0x08) # RDIV, NDIV[9:8], (RDIV =2 --> 0x08, RDIV=3-->0x0C, RDIV=6 --> 0x18)
    device.SPIWriteByte(0x06 << 1, 0x06) # RDIV
    device.SPIWriteByte(0x07 << 1, 0x07) #
    device.SPIWriteByte(0x08 << 1, 0x01) # out0: muted
    device.SPIWriteByte(0x09 << 1, 0x13) # out0: 300MHz
    device.SPIWriteByte(0x0A << 1, 0xC0) #
    device.SPIWriteByte(0x0B << 1, 0x9B) # out1: 18.75M (FPGA SYSREF)
    device.SPIWriteByte(0x0C << 1, sysref_delay) # delay out1: 23 f0r 300
    device.SPIWriteByte(0x0D << 1, 0x93) # out2: 300M (ADC clock 1)
    device.SPIWriteByte(0x0E << 1, clk_delay) # delay out2: 1E for 300
    device.SPIWriteByte(0x0F << 1, 0x9B) # out3: 18.75M (adc sysref_1)
    device.SPIWriteByte(0x10 << 1, sysref_delay) # delay out3: 23 for 300
    device.SPIWriteByte(0x11 << 1, 0x30) # out4: div and out powered down (0x30)
    device.SPIWriteByte(0x12 << 1, 0x00) #
    device.SPIWriteByte(0x13 << 1, 0x11) #
    device.SPIWriteByte(0x02 << 1, 0x01) # calibrate after writing all registers
    

    print "toggle SYNC cp"
    sleep(sleeptime)
    device.FPGAWriteAddress(SPI_CONFIG_REG) #Assert EZsync
    print "sync high"
    device.FPGAWriteData(0x08)  # only toggle LTC6951 sync (LTC6954 does not need a sync with DIV=1)
    sleep(sleeptime)
    print "sync low"
    device.FPGAWriteData(0x00)
    sleep(sleeptime)
	
	
# After the LTC6951's are SYNC'd the CMOS outputs of the LTC6954 can be powered down 
# Powering down the LTC6954 CMOS output, sets them to a static level (low or high)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x04) ## VERIFIED!! ##
    device.SPIWriteByte(0x00 << 1, 0x10)  # power down LTC6954 output2 
	
	
def LTC6951_powerdown_JESDclocks(device, K, verbose):
    if(verbose != 0):
        print "Configuring clock generators over SPI:"
    device.SetMode(device.ModeMPSSE)
	

# LTC6951 are adjusted for the 60MHz reference input	
# LTC6951config - this one controls the out2 and out3 ADC (out2 and out3 refer to plot order)
    print "Configuring U10 (LTC6951) cp"
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x02) ## VERIFIED!! ##
    device.SPIWriteByte(0x0B << 1, 0xBB) # out1: 18.75M (sysref2)
	
    print "Configuring U13 (LTC6951) cp"
# LTC6951config - this one controls the out0 and out1 ADC (out0 and out1 refer to plot order)
# in other words this is the one with the fs/3-fin mixing spurs
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x03) ## VERIFIED!! ##

    device.SPIWriteByte(0x0B << 1, 0xBB) # out1: 18.75M (FPGA SYSREF)
    device.SPIWriteByte(0x0F << 1, 0xBB) # out3: 18.75M (ADC1 SYSREF)

def Print_spec_data(data_ch0, runs):
    x = "a_ch0_filton_27p4"
    y = str(runs)
    chanxy = x + y
    f = open(chanxy, "w")
    f.write('Version,115\n')
    f.write('Retainers,0,1,32768,1024,6,300.000000000000000,0,1\n')
    f.write('Placement,44,0,1,-1,-1,-1,-1,419,16,1440,740\n')
    f.write('WindMgr,6,2,0\n')
    f.write('Page,0,2\n')
    f.write('Col,3,1\n')
    f.write('Row,2,1\n')
    f.write('Row,3,146\n')
    f.write('Row,1,319\n')
    f.write('Col,2,777\n')
    f.write('Row,4,1\n')
    f.write('Row,0,319\n')
    f.write('Page,1,2\n')
    f.write('Col,1,1\n')
    f.write('Row,1,1\n')
    f.write('Col,2,777\n')
    f.write('Row,4,1\n')
    f.write('Row,0,319\n')
    f.write('DemoID,DC1509,LTC2107,0\n')
    f.write('RawData,1,32768,16,4371,61253,300.000000000000000,0.000000e+000,6.553600e+004	\n')	
    for i in range(0, 32768):
        f.write(str(data_ch0[i]))      # str() converts to string
        f.write('\n')


    f.write('End			\n')	
    f.close()