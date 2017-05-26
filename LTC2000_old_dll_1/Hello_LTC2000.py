#Getting started on the LTC2000!!
from time import sleep

import sys
sys.path.append("../modules/FTSyncFifoDevicePy")

#from LTC2000_functions import *
import LTC2000_functions as lt2k
from math import sin


numcycles = 1000 #Number of sinewave cycles over the entire data record
verbose = 1
sleeptime = 1.0

if(verbose != 0):
    print "LTC2000 Interface Program"
    
try:
    device = lt2k.open_LTC2000_comms_and_reset(1)
    device.SetMode(device.ModeMPSSE)
    device.SetReset(device.PinStateLow) #Issue reset pulse
    device.SetReset(device.PinStateHigh)

    device.FPGAWriteAddress(lt2k.FPGA_ID_REG)
    id = device.FPGAReadData()
    if(verbose != 0):
        print "FPGA Load ID: 0x{:04X}".format(id)    
        print "Reading PLL status, should be 0x57"
        device.FPGAWriteAddress(lt2k.FPGA_STATUS_REG)
        data = device.FPGAReadData()
        print "And it is... 0x{:04X}".format(data)    
        print "Turning on DAC..."
    
    device.SetMode(device.ModeMPSSE)
    device.FPGAWriteAddress(lt2k.FPGA_DAC_PD)
    device.FPGAWriteData(0x01)  #Turn on DAC

    sleep(sleeptime)

    if(verbose != 0):
        print "Configuring ADC over SPI:"
    device.SetMode(device.ModeMPSSE)

    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_RESET_PD, 0x00)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_CLK_CONFIG, 0x02)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_CLK_PHASE, 0x07)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_PORT_EN, 0x0B)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_SYNC_PHASE, 0x00)
#    device.SPIWriteByte(REG_PHASE_COMP_OUT
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_LINER_GAIN, 0x00)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_LINEARIZATION, 0x08)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_DAC_GAIN, 0x20)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_LVDS_MUX, 0x00)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_TEMP_SELECT, 0x00)
    device.SPIWriteByte(lt2k.SPI_WRITE | lt2k.REG_PATTERN_ENABLE, 0x00)
#    device.SPIWriteByte(REG_PATTERN_DATA
       
    sleep(sleeptime) # Give some time for things to spin up...
    
    if(verbose != 0):
        lt2k.LTC2000_register_dump(device)
        
    device.FPGAWriteAddress(lt2k.FPGA_CONTROL_REG) #FPGA control / size register
    device.FPGAWriteData(0x20 | 0x00) # 64k, loop forever
    
    sleep(sleeptime)
        
    totSamps = 65536#n.BuffSize
    data = totSamps * [0] 
    for i in range(0, totSamps):
        data[i] = int(32000*sin(numcycles*2*3.141592653*i/totSamps)) #+ 32768
        #data[i] = (data[i] >> 8) & 0x00FF | (data[i] << 8)
    
    device.SetMode(device.ModeFIFO)
    device.FIFOSendUShorts(data) #DAC should start running here!
    
finally:
    device.Close()

