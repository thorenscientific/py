# -*- coding: utf-8 -*-
"""
Support functions and definitions for the LTC2000
"""

import sys
sys.path.append("../modules/FTSyncFifoDevicePy")
import FTSyncFifoDevicePy

###################################
#LTC2000 SPI register definitions #
###################################
REG_RESET_PD        = 0x01
REG_CLK_CONFIG      = 0x02
REG_CLK_PHASE       = 0x03
REG_PORT_EN         = 0x04
REG_SYNC_PHASE      = 0x05
REG_PHASE_COMP_OUT  = 0x06
REG_LINER_GAIN      = 0x07
REG_LINEARIZATION   = 0x08
REG_DAC_GAIN        = 0x09
REG_LVDS_MUX        = 0x18
REG_TEMP_SELECT     = 0x19
REG_PATTERN_ENABLE  = 0x1E
REG_PATTERN_DATA    = 0x1F

SPI_READ = 0x80 #OR with register
SPI_WRITE = 0x00

#############################
# FPGA register definitions #
#############################

FPGA_ID_REG = 0x00
# Initial release - 0x1A

FPGA_CONTROL_REG = 0x01
# Bit         7  6   5   4       3   2   1       0      
# Bit Name    MEMSIZE            RSV             MODE       
# Read/Write    Write      
# Initial Value 0x00

# MODE = 0 - continuous playback
# MODE = 1 - play data once

# MEMSIZE options - OR with FPGA_CONTROL_REG 
# 0x00  2^14 samples (16k)
# 0x10  2^15 samples (32k)
# 0x20  2^16 samples (64k)
# 0x30  2^17 samples (128k)
# 0x40  2^18 samples (256k)
# 0x50  2^19 samples (512k)
# 0x60  2^20 samples (1M)
# 0x70  2^21 samples (2M)
# 0x80  2^22 samples (4M)
# 0x90  2^23 samples (8M)
# 0xA0  2^24 samples (16M)
# 0xB0  2^25 samples (32M)
# 0xC0  2^26 samples (64M)
# 0xD0  2^27 samples (128M)
# 0xE0  2^28 samples (256M)

FPGA_STATUS_REG = 0x02
# Bit 6 -    FWRFUL: The FIFO writing data to external DDR3 is full.
# Bit 5 -    FRDFUL: The FIFO reading data from external DDR3 is full.
# Bit 4 -    DDRPLL: The embedded PLL of the DDR controller is locked.
# Bit 3 -    DDRRDY: External DDR is ready to access.
# Bit 2 -    PLL0: The PLL accepting SYSCLK is locked. 
# Bit 1 -    PLL1: The PLL accepting DDCK is locked. 
# Bit 0 -    PLL2: The PLL accepting fifoclk is locked. 

FPGA_DAC_PD = 0x03
# Bit 0 (DACPD) = 0 - Turn OFF DAC
# Bit 0 (DACPD) = 1 - Turn ON DAC


def LTC2000_register_dump(device):
    print "LTC2000 Register Dump: " 
    print "Register 0: 0x{:02X}".format(device.SPIReadByte(0x80))
    print "Register 1: 0x{:02X}".format(device.SPIReadByte(0x81))
    print "Register 2: 0x{:02X}".format(device.SPIReadByte(0x82))
    print "Register 3: 0x{:02X}".format(device.SPIReadByte(0x83))
    print "Register 4: 0x{:02X}".format(device.SPIReadByte(0x84))
    print "Register 5: 0x{:02X}".format(device.SPIReadByte(0x85))
    print "Register 6: 0x{:02X}".format(device.SPIReadByte(0x86))
    print "Register 7: 0x{:02X}".format(device.SPIReadByte(0x87))
    print "Register 8: 0x{:02X}".format(device.SPIReadByte(0x88))
    print "Register 9: 0x{:02X}".format(device.SPIReadByte(0x89))


def open_LTC2000_comms_and_reset(res):
    device = FTSyncFifoDevicePy.FTSyncFifoDevice()
    device.OpenByDescription(['LTC2000, DC2085A-A', 'LTC Communication Interface', 'LTC2000 Demoboard'])
    serial = device.GetSerialNumber()
    device.SetMode(device.ModeMPSSE)
    if(res == 1):
        device.SetReset(device.PinStateLow) #Issue reset pulse
        device.SetReset(device.PinStateHigh)
    return device