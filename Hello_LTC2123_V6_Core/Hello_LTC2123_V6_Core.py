
import sys
sys.path.append("../modules/FTSyncFifoDevicePy")
sys.path.append("../modules/LTC2123_functions")

import FTSyncFifoDevicePy
from LTC2123_functions import *

continuous = 0
runs = 0
runs_with_errors = 0
runs_with_uncaught_errors = 0

errorcount = 0

initialize_spi = 1
initialize_core = 1
initialize_reset = 1

channels = 3 # options: 1 for channel 1, 2 for channel 2, 3 for both.
lanes = 2
subclass = 0
verbose = 1

patterncheck = 32 #Enable PRBS check, ADC data otherwise
dumppattern = 32 #Dump pattern analysis

dumpdata = 32 # Set to 1 and select an option below to dump to STDOUT:
hex = 1     # Data dump format, can be either hex, decimal, or both
dec = 0     # (if both, hex is first, followed by decimal)

dump_pscope_data = 1 # Writes data to "pscope_data.csv", append to header to open in PScope

n = NumSamp128K # Set number of samples here.

#Configure other ADC modes here to override ADC data / PRBS selection
forcepattern = 0    #Don't override ADC data / PRBS selection
#forcepattern = 0x04 #PRBS
#forcepattern = 0x06 #Test Samples test pattern
#forcepattern = 0x07 #RPAT test pattern
#forcepattern = 0x02 # K28.7 (minimum frequency)
#forcepattern = 0x03 # D21.5 (maximum frequency)

sleeptime = 0.1

#device = open_UFO_and_reset(1)
#initialize_reset = 0
#device.Close()
device = None


while((runs < 1 or continuous == 1) and runs_with_errors < 100000):
    runs += 1
#    if(verbose != 0):
    print "LTC2124 Interface Program"
    print "Run number: " + str(runs)
    print "\nRuns with errors: " + str(runs_with_errors) + "\n"
    if (runs_with_uncaught_errors > 0):
        print "***\n***\n***\n*** UNCAUGHT error count: " + str(runs_with_uncaught_errors) + \
        "!\n***\n***\n***\n"

    ################################################
    # Configuration Flow Step 6: Issue Reset Pulse
    ################################################
    
    if device == None:
        device = open_UFO_and_reset(initialize_reset)
        initialize_reset = 0

    ################################################
    # Configuration Flow Step 7, 8:
    # Check ID and Clock Status register
    ################################################
    device.FPGAWriteAddress(ID_REG)
    id = device.FPGAReadData()
    if(verbose != 0):
        print "FPGA Load ID: 0x{:04X}".format(id)
        sleep(sleeptime)
        print "Dumping readable FPGA registers"
        device.FPGAWriteAddress(CAPTURE_STATUS_REG)
        data = device.FPGAReadData()
        print "Register 4 (capture status): 0x{:04X}".format(data)
        device.FPGAWriteAddress(CLOCK_STATUS_REG)
        data = device.FPGAReadData()
        print "Register 6   (Clock status): 0x{:04X}".format(data)
        sleep(sleeptime)

    ################################################
    # Configuration Flow Step 9, 10: Configure ADC
    ################################################
    if(initialize_spi == 1):
        if(verbose != 0):
            print "Configuring ADC over SPI:"
        device.SetMode(device.ModeMPSSE)

    #    device.SPIWriteByte(0x00, 0x01) # reset dut
        device.SPIWriteByte(0x03, 0xAB) #Device ID to 0x34
        device.SPIWriteByte(0x04, 0x01) #Bank ID to 0x01

        if(lanes == 2):
            device.SPIWriteByte(0x05, 0x01) #2 lane mode (default)
        else:
            device.SPIWriteByte(0x05, 0x00) #1 lane mode (2 ADCs - 1 lane)

        device.SPIWriteByte(0x06, 0x09) #10 frames / multiframe (0x09)
    #    device.SPIWriteByte(0x06, 0x10)

        #device.SPIWriteByte(0x07, 0x00) #Enable FAM, LAM
        device.SPIWriteByte(0x07, 0x18) #Disable FAM, LAM (only needed for prerelease silicon)

        #device.SPIWriteByte(0x08, 0x00)

        if(patterncheck != 0):
            device.SPIWriteByte(0x09, 0x04) #PRBS test pattern
        else:
            device.SPIWriteByte(0x09, 0x00) #Normal ADC data

        if(forcepattern != 0):
            device.SPIWriteByte(0x09, forcepattern)

#    dump_ADC_registers(device)


    ################################################
    # Configuration Flow Step 11: configure JEDEC Core
    ################################################
    if(initialize_core == 1):
        if(verbose != 0):
            print "Configuring JESD204B core!!"
        write_jesd204b_reg(device, 0x08, 0x00, 0x00, 0x00, 0x01)
        write_jesd204b_reg(device, 0x0C, 0x00, 0x00, 0x00, 0x00)
        write_jesd204b_reg(device, 0x10, 0x00, 0x00, 0x00, 0x01)
        write_jesd204b_reg(device, 0x18, 0x00, 0x00, 0x00, 0x00)
        write_jesd204b_reg(device, 0x20, 0x00, 0x00, 0x00, 0x01)
        write_jesd204b_reg(device, 0x24, 0x00, 0x00, 0x00, 0x09)
        write_jesd204b_reg(device, 0x28, 0x00, 0x00, 0x00, 0x00) # Lanes in use - program with N-1
        write_jesd204b_reg(device, 0x2C, 0x00, 0x00, 0x00, 0x00)
        write_jesd204b_reg(device, 0x30, 0x00, 0x00, 0x00, 0x00)
        write_jesd204b_reg(device, 0x34, 0x00, 0x00, 0x00, 0x00)
        write_jesd204b_reg(device, 0x04, 0x00, 0x00, 0x00, 0x01)

        



    device.FPGAWriteAddress(CLOCK_STATUS_REG)
    data = device.FPGAReadData()
    print "Double-checking clock status after JESD204B configuration:"
    print "Register 6   (Clock status): 0x{:04X}".format(data)


    if(verbose != 0):
        print "Capturing data and resetting..."

    data, data_ch0, data_ch1, nSamps_per_channel, syncErr = capture(device, n, channels, lanes, dumpdata, dump_pscope_data, verbose)

#    data, data_ch0, data_ch1, nSamps_per_channel = capture(device, n, channels, lanes, dumpdata, dump_pscope_data, verbose)

    if(patterncheck !=0):
        errorcount = pattern_checker(data_ch0, nSamps_per_channel, dumppattern)
        errorcount += pattern_checker(data_ch1, nSamps_per_channel, dumppattern)


    if(errorcount != 0):
        outfile = open("LTC2123_python_error_log.txt", "a")
        outfile.write("Caught " + str(errorcount) + "errors on run " + str(runs) + "\n")
        byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, 0x24)
        outfile.write("Register 0x24, all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0))
        byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, 0x27)
        outfile.write("Register 0x27, all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0))
        
        outfile.close()
        
        outfile = open("error_data_run_" + str(runs) + ".csv", "w")
        outfile.write("channel1, channel2\n")
        for i in range(0, nSamps_per_channel):
            #print "{:d}, ,0".format((data[i]-32768)/4)
            outfile.write(str(data_ch0[i]) + ", " + str(data_ch1[i]) + "\n")
        #print "End"
        #outfile.write("End\n")
        outfile.close()        
        
        
        runs_with_errors += 1
        if (syncErr == False):
            runs_with_uncaught_errors += 1
    print "error count: " + str(errorcount) + " !"

    if(verbose != 0):
        print "Verifying registers 0-0x3C:"
        device.FPGAWriteAddress(0x13) # R2INDEX - extends 
        device.FPGAWriteData(0x00)
        for reg in range(0, 16):
            byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, reg * 4)
            print "Register " + '{:02X}'.format(reg * 4) + " , all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0)

        print "Verifying registers 0x800 - 0x87C (ILAS):"
        device.FPGAWriteAddress(0x13) # R2INDEX - extends address
        device.FPGAWriteData(0x20)
# Fix me!! symbolically shift upper bits and write to R2INDEX
        for reg in range(512, 544):
            byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, reg * 4)
            print "Register " + '{:02X}'.format(reg * 4) + " , all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0)


    print "\n"
            
    device.Close() #End of main loop.
    device = None

    
    

