import sys
sys.path.append("../modules/LTC2123_functions")
sys.path.append("../modules/FTSyncFifoDevicePy")
from LTC2123_functions import *
import FTSyncFifoDevicePy



def wadc1():        
    device = open_UFO_and_reset(0)
    print "Configuring ADC1 over SPI:"
    device.SetMode(device.ModeMPSSE)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x00)

#    device.SPIWriteByte(0x00, 0x01) # reset dut
    device.SPIWriteByte(0x03, 0xAB) #Device ID to 0xAB
    device.SPIWriteByte(0x04, 0x01) #Bank ID to 0x01
    device.SPIWriteByte(0x05, 0x01) #2 lane mode (default)
#    device.SPIWriteByte(0x06, 0x1F) #9 frames / multiframe (0x08)
    device.SPIWriteByte(0x06, 0x09)
    device.SPIWriteByte(0x07, 0x00) #Enable FAM, LAM
    #device.SPIWriteByte(0x07, 0x18) #Disable FAM, LAM (only needed for prerelease silicon)
    device.SPIWriteByte(0x08, 0x01)
    device.SPIWriteByte(0x09, 0x04) #PRBS test pattern
   # device.SPIWriteByte(0x09, 0x00) #Normal ADC data
    device.SPIWriteByte(0x0A, 0x03) # 0x03 = 16mA CML current
    device.Close()
    print "done"

def wadc2():
      
    device = open_UFO_and_reset(0)
    print "Configuring ADC2 over SPI:"
    device.SetMode(device.ModeMPSSE)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x01)  
#    device.SPIWriteByte(0x00, 0x01) # reset dut
    device.SPIWriteByte(0x03, 0xCD) #Device ID to 0xAB
    device.SPIWriteByte(0x04, 0x01) #Bank ID to 0x01
    device.SPIWriteByte(0x05, 0x01) #2 lane mode (default)
#    device.SPIWriteByte(0x06, 0x1F) #9 frames / multiframe (0x08)
    device.SPIWriteByte(0x06, 0x09)
    device.SPIWriteByte(0x07, 0x00) #Enable FAM, LAM
    #device.SPIWriteByte(0x07, 0x18) #Disable FAM, LAM (only needed for prerelease silicon)
    device.SPIWriteByte(0x08, 0x01)
    device.SPIWriteByte(0x09, 0x04) #PRBS test pattern
   # device.SPIWriteByte(0x09, 0x00) #Normal ADC data
    device.SPIWriteByte(0x0A, 0x03) # 0x03 = 16mA CML current
    device.Close()
    print "done."

def radc1():
    device = open_UFO_and_reset(0)
    print "ADC 1 configuration dump:"
    dump_ADC_registers(device)
    device.Close()

def radc2():
    device = open_UFO_and_reset(0)
    print "ADC 2 configuration dump:"
    dump_ADC_registers(device)
    device.Close()


def wrefclk(): 
    device = open_UFO_and_reset(0)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x02)  
#LTC6950 config
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
    device.SPIWriteByte(0x10 << 1, 0x80) #
    device.SPIWriteByte(0x11 << 1, 0x84) # Clock to SYSREF gen (LTC6954)
    device.SPIWriteByte(0x12 << 1, 0x80) #
#        device.SPIWriteByte(0x13 << 1, 0x84) #
    device.SPIWriteByte(0x13 << 1, 0x84) # FPGA device clock
    device.SPIWriteByte(0x14 << 1, 0x80) #
    device.SPIWriteByte(0x15 << 1, 0x04) #

    device.Close()
    
def rrefclk():
    device = open_UFO_and_reset(0)
    print "dumping refclk registers (LTC6950)"
    for i in range(0, 0x17):
        print "Register {:d}: 0x{:02X}".format(i, device.SPIReadByte((i<<1) + 1))
    device.Close()
    
def wsysrefclk(): 
    device = open_UFO_and_reset(0)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x03)  
#LTC6954 config
    device.SPIWriteByte(0x00 << 1, 0x00) # Dumb values to div by 32,
    device.SPIWriteByte(0x01 << 1, 0xC0) # EZSync!!!
    device.SPIWriteByte(0x02 << 1, 0x0A) #
    device.SPIWriteByte(0x03 << 1, 0xC0) #
    device.SPIWriteByte(0x04 << 1, 0x0A) #
    device.SPIWriteByte(0x05 << 1, 0xC0) #
    device.SPIWriteByte(0x06 << 1, 0x0A) #
    device.SPIWriteByte(0x07 << 1, 0x20) #
    device.Close()

def rsysrefclk():
    device = open_UFO_and_reset(0)
    print "dumping refclk registers (LTC6954)"
    for i in range(0, 0x08):
        print "Register {:d}: 0x{:02X}".format(i, device.SPIReadByte((i<<1) + 1))
    device.Close()
    
    
    
def configcore():
    device = open_UFO_and_reset(0)
    print "Configuring JESD204B core!!"
    write_jesd204b_reg(device, 0x01, 0, 0, 0, 0x01) # 2 lane
    write_jesd204b_reg(device, 0x02, 0, 0, 0, 0x00)
    write_jesd204b_reg(device, 0x03, 0, 0, 0, 0x09) # 9 frames / multiframe
#    write_jesd204b_reg(device, 0x03, 0, 0, 0, 0x10)
#    write_jesd204b_reg(device, 0x00, 0, 0, 0x02, 0x82) # 0x82 to reset, 0x02 to NOT reset, 2 lanes in use
#    write_jesd204b_reg(device, 0x00, 0, 0, 0x02, 0x83) # 0x82 to reset, 0x02 to NOT reset, 2 lanes in use ENABLE DESCRAMBLER
    write_jesd204b_reg(device, 0x00, 0, 0, 0x03, 0x82) # 0x82 to reset, 0x02 to NOT reset, 1 lane in use, enable link test
    device.Close()
    
    
def cs2check(): 
    device = open_UFO_and_reset(0)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x02)  
    device.SPIWriteByte((0x00 << 1) + 1, 0x00) # Dumb values to div by 32,
    device.SPIWriteByte((0x00 << 1) + 1, 0x00) # Dumb values to div by 32,
    device.Close()
    
def cs3check(): 
    device = open_UFO_and_reset(0)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x03)  
    device.SPIWriteByte((0x00 << 1) + 1, 0x00) # Dumb values to div by 32,
    device.SPIWriteByte((0x00 << 1) + 1, 0x00) # Dumb values to div by 32,
    device.Close()
    
def cs4check(): 
    device = open_UFO_and_reset(0)
    device.FPGAWriteAddress(SPI_CONFIG_REG)
    device.FPGAWriteData(0x04)  
    device.SPIWriteByte((0x00 << 1) + 1, 0x00) # Dumb values to div by 32,
    device.SPIWriteByte((0x00 << 1) + 1, 0x00) # Dumb values to div by 32,
    device.Close()
    