import sys
sys.path.append("../modules/LTC2123_functions")
sys.path.append("../modules/FTSyncFifoDevicePy")
from LTC2123_functions import *
import FTSyncFifoDevicePy


continuous = 0
runs = 0
runs_with_errors = 0
runs_with_uncaught_errors = 0

errorcount = 0

initialize_adcs = 1
initialize_clocks = 1

initialize_core = 1
initialize_reset = 1

lanes = 2
verbose = 1
plot_data = 1

patterncheck = 0 #Enable PRBS check, ADC data otherwise
dumppattern = 1000 #Dump pattern analysis

dumpdata = 128 # Set to 1 and select an option below to dump to STDOUT:
hexdump = 1     # Data dump format, can be either hex, decimal, or both
dec = 0     # (if both, hex is first, followed by decimal)

dump_pscope_data = 1 # Writes data to "pscope_data.csv", append to header to open in PScope

n = NumSamp1K
 # Set number of samples here.

#Configure other ADC modes here to override ADC data / PRBS selection
forcepattern = 0    #Don't override ADC data / PRBS selection
#forcepattern = 0x04 #PRBS
#forcepattern = 0x06 #Test Samples test pattern
#forcepattern = 0x07 #RPAT test pattern
#forcepattern = 0x02 # K28.7 (minimum frequency)
#forcepattern = 0x03 # D21.5 (maximum frequency)

K = 32 #Frames per multiframe

did0=0xEF
did1=0xAB
bid=0x00
modes=0x00
pattern0=0x07
pattern1=0x07


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
    # Configuration Flow Steps 4, 5: 
    # MPSSE Mode, Issue Reset Pulse
    ################################################
    
    if device == None:
        print("Opening FTDI interface, reset = ") + str(initialize_reset)
        device = open_UFO_and_reset(initialize_reset)
        initialize_reset = 0

    ################################################
    # Configuration Flow Step 6:
    # Check ID register
    ################################################
    device.FPGAWriteAddress(ID_REG)
    id = device.FPGAReadData()
    if(verbose != 0):
        print "FPGA Load ID: 0x{:04X}".format(id)


    ################################################
    # Configuration Flow Step 9, 10: Configure ADC
    ################################################



    if(initialize_adcs == 1):
        load_ltc212x(device, 0, verbose, 0xCD, bid, K, modes, pattern0)
        load_ltc212x(device, 1, verbose, 0xAB, bid, K, modes, pattern1)

    if(initialize_clocks == 1):
        initialize_DC2226_clocks(device, K, verbose)


# Okay, now disable ADC sensitivity to SYSREF:
#    device.SetMode(device.ModeMPSSE)
#    device.FPGAWriteAddress(SPI_CONFIG_REG)
#    device.FPGAWriteData(0x00) #ADC 1
#    device.SPIWriteByte(0x07, 0x1A) #Enable FAM, LAM, DISABLE SYSREF
#    device.FPGAWriteData(0x01) #ADC 1
#    device.SPIWriteByte(0x07, 0x1A) #Enable FAM, LAM, DISABLE SYSREF
#    sleep(sleeptime)


    ################################################
    # Configuration Flow Step 11: Reset Capture Engine
    ################################################
    device.FPGAWriteAddress(CAPTURE_RESET_REG) 
    device.FPGAWriteData(0x01)  #Reset

    ################################################
    # Configuration Flow Step 19: Check Clock Status
    ################################################

    if(verbose != 0):
        print "Reading Clock Status register; should be 0x16 (or at least 0x04 bit set)"
        device.FPGAWriteAddress(CLOCK_STATUS_REG)
        data = device.FPGAReadData()
        print "Register 6   (Clock status): 0x{:04X}".format(data)
        sleep(sleeptime)

    ################################################
    # Configuration Flow Step 11: configure JEDEC Core
    ################################################
    if(initialize_core == 1):
        if(verbose != 0):
            print "Configuring JESD204B core!!"
        write_jesd204b_reg(device, 0x01, 0, 0, 0, 0x01) # 2 lane
        write_jesd204b_reg(device, 0x02, 0, 0, 0, 0x00)
        write_jesd204b_reg(device, 0x03, 0, 0, 0, 0x1F) # K=10 frames / multiframe
    #    write_jesd204b_reg(device, 0x03, 0, 0, 0, 0x10) # K=17 frames / multiframe
    #    write_jesd204b_reg(device, 0x00, 0, 0, 0x03, 0x82) # 0x00000382 = 4 lanes, reset, first SYSREF only, enable SYNC
        write_jesd204b_reg(device, 0x00, 0, 0, 0x13, 0x82)




    if(verbose != 0):
        print "Capturing data and resetting..."

    data_ch0, data_ch1, data_ch2, data_ch3, nSamps_per_channel, syncErr = capture4(device, n, lanes, dumpdata, dump_pscope_data, verbose)


    if(patterncheck !=0):
        errorcount = pattern_checker(data_ch0, nSamps_per_channel, dumppattern)
        errorcount += pattern_checker(data_ch1, nSamps_per_channel, dumppattern)
        errorcount += pattern_checker(data_ch2, nSamps_per_channel, dumppattern)
        errorcount += pattern_checker(data_ch3, nSamps_per_channel, dumppattern)


    if(errorcount != 0):
        outfile = open("LTC2123_python_error_log.txt", "a")
        outfile.write("Caught " + str(errorcount) + "errors on run " + str(runs) + "\n")
        byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, 0x24)
        outfile.write("Register 0x24, all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0))
        byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, 0x27)
        outfile.write("Register 0x27, all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0))
        
        outfile.close()
        
#    #Don't write a file each time!!        
#        outfile = open("error_data_run_" + str(runs) + ".csv", "w")
#        outfile.write("channel1, channel2\n")
#        for i in range(0, nSamps_per_channel):
#            #print "{:d}, ,0".format((data[i]-32768)/4)
#            outfile.write(str(data_ch0[i]) + ", " + str(data_ch1[i]) + "\n")
#        #print "End"
#        #outfile.write("End\n")
#        outfile.close()        
       

        runs_with_errors += 1
        if (syncErr == False):
            runs_with_uncaught_errors += 1
    print "error count: " + str(errorcount) + " !"

    if(verbose != 0):
        print "Verifying registers 0x00 - 0x13:"
        for reg in range(0, 0x14):
            byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, reg)
            print "Register " + '{:02X}'.format(reg) + " , all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0)

        print "Test Mode Error Count registers for lanes 0-3:"
        for i in range(0, 4):
            reg = (0x24 + (i * 3))
            byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, reg)
            print "Register " + '{:02X}'.format(reg) + " , all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0)

        print "rx_buffer_adjust for lanes 0, 1"
        reg = 0x3C
        byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, reg)
        print "Register " + '{:02X}'.format(reg) + " , all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0)
        print "rx_buffer_adjust for lanes 2,3"
        reg = 0x3D
        byte3, byte2, byte1, byte0 = read_jesd204b_reg(device, reg)
        print "Register " + '{:02X}'.format(reg) + " , all bytes: " + ' {:02X} {:02X} {:02X} {:02X}'.format(byte3, byte2, byte1, byte0)

    if(plot_data != 0):
        from matplotlib import pyplot as plt
        plt.figure(1)
        plt.subplot(411)
        plt.plot(data_ch0)
        plt.title('CH0')
        plt.subplot(412)
        plt.title('CH1')
        plt.plot(data_ch1)
        plt.subplot(413)
        plt.title('CH2')
        plt.plot(data_ch2)
        plt.subplot(414)
        plt.title('CH3')
        plt.plot(data_ch3)
        plt.show()

    print "\n"
            
    device.Close() #End of main loop.
    device = None

    
    

