%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SPI read / write bit definitions %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
SPI_READ = 128; % OR with register
SPI_WRITE = 0;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% LTC2000 SPI register definitions %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
REG_RESET_PD            = 1;
REG_CLK_CONFIG          = 2;
REG_CLK_PHASE           = 3;
REG_PORT_EN             = 4;
REG_SYNC_PHASE          = 5;
REG_PHASE_COMP_OUT      = 6;
REG_LINER_GAIN          = 7;
REG_LINEARIZATION       = 8;
REG_DAC_GAIN            = 9;
REG_LVDS_MUX            = 24;
REG_TEMP_SELECT         = 25;
REG_PATTERN_ENABLE      = 30;
REG_PATTERN_DATA        = 31;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% LTC2000 bit field definitions %
% High bit value ENABLES feature unless
% otherwise noted.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% REG_RESET_PD (0x01)
RESET_PD_ALL_ON         = 0; % Write zero for normal operation
RESET_PD_SW_RST         = 1; % Software reset all registers
RESET_PD_DACPD          = 2; % DAC power-down
RESET_PD_FULL_PD        = 4; % Full power-down
RESET_PD_RES_MASK       = 48; % AND with REG_RESET_PD to extract resolution indicator

% REG_CLK_CONFIG (0x02)
CLK_CONFIG_CK_PD        = 1; % Power down 
CLK_CONFIG_CK_OK_MASK   = 2; % AND with REG_CLK_CONFIG, high indicates clock present
CLK_CONFIG_DCKO_DIS     = 16; % Disable DCKO
CLK_CONFIG_DCKO_DIV     = 32; % DCKO divide select: 0 = fDAC/4, 1 = fDAC/2
CLK_CONFIG_DCKO_ISEL    = 64; % LVDS Output current: 0=3.5mA, 1=7mA
CLK_CONFIG_DCKO_TRM     = 128; % Enable internal 100 ohm termination

% REG_DCKI_PHASE       (0x03)
DCKI_PHASE_DCKI_EN      = 1; %
DCKI_PHASE_DCKI_OK_MASK = 2; %
DCKI_PHASE_DCKI_Q       = 4; % 
DCKI_PHASE_DCKI_TADJ_230PS = 96; % DCKI Phase adjustment
DCKI_PHASE_DCKI_TADJ_315PS = 112; % No effect when DCKI_Q = 1
DCKI_PHASE_DCKI_TADJ_400PS = 0; %
DCKI_PHASE_DCKI_TADJ_485PS = 16; %
DCKI_PHASE_DCKI_TADJ_570PS = 32; %

% REG_PORT_EN          (0x04)
PORT_EN_DA_EN           = 1; % Port A LVDS Receiver Enable
PORT_EN_DB_EN           = 2; % Port B LVDS Receiver Enable
PORT_EN_DATA_SP         = 3; % Port mode select: 0=dual port, 1=single port
PORT_EN_DATA_EN         = 4; % DAC Data enable. De-assert to force DAC output to mid-scale

% REG_SYNC_PHASE       (0x05)
% Bits [1:0] set synchronizer phase when SYNC_PHASE_SYNC_MSYN is asserted
SYNC_PHASE_SYNC_MSYN    = 4;

% REG_PHASE_COMP_OUT   (0x06)
% Entire register represents phase comparator output.

% REG_LINER_GAIN       (0x07)
LINER_GAIN_LIN_DIS      = 1; % Disable dynamic linearization
LINER_GAIN_LIN_GN_50    = 12; % 50% Linearization Percentage
LINER_GAIN_LIN_GN_63    = 14; % 63% Linearization Percentage
LINER_GAIN_LIN_GN_75    = 0; % 75% Linearization Percentage
LINER_GAIN_LIN_GN_88    = 2; % 88% Linearization Percentage
LINER_GAIN_LIN_GN_100   = 4; % 100% Linearization Percentage
LINER_GAIN_LIN_GN_113   = 6; % 113% Linearization Percentage
LINER_GAIN_LIN_GN_125   = 8; % 125% Linearization Percentage
LINER_GAIN_LIN_GN_138   = 10; % 138% Linearization Percentage

% REG_LINEARIZATION    (0x08)
% Upper and lower nibbles correspond to LIN_VMN and LIN_VMX, respectively.
% Refer to datasheet table 7.

% REG_DAC_GAIN         (0x09)
% Lower 6 bits are a 2's complement number mapped as such:
% +31: 89.2% Gain Adjustment
% +30: 89.5%
% ---------
% +1: 99.6%
% 0: 100%
% -1: 100.4%
% ---------
% -31: 113.8%
% -32: 114.3%

% (Double-check - you should be able to treat this as an 8 bit integer
% and just truncate)

% REG_LVDS_MUX         (0x18)
LVDS_MUX_LMX_MSEL       = 1; % Select which member of a pair of signals to select
LVDS_MUX_LMX_ADR_MASK   = 62; % 6 bit address, see table 8
LVDS_MUX_LMX_EN         = 64; % LVDS test mux enable

% REG_TEMP_SELECT      (0x19)
TEMP_SELECT_TDIO_EN     = 1; % Enable junction temp. diode (make sure LMX_EN = 0)
TEMP_SELECT_TDIO_SELECT = 2; % Select mode: 0=NPN xistor, 1=voltage

% REG_PATTERN_ENABLE   (0x1E)
PATTERN_ENABLE_PGEN_EN  = 1; % Enable pattern generator from internal memory

% REG_PATTERN_DATA     (0x1F)
% Send 128 bytes of data to this register. Data is MSB first, 64 total samples

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% FPGA register definitions %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

FPGA_ID_REG             = 0;
% Initial release - 0x1A

FPGA_CONTROL_REG        = 1;
% Bit         7  6   5   4       3   2   1       0      
% Bit Name    MEMSIZE            RSV             MODE       
% Read/Write    Write      
% Initial Value 0x00

% MODE = 0 - continuous playback
% MODE = 1 - play data once

% MEMSIZE options - OR with FPGA_CONTROL_REG 
% 0x00  2^14 samples (16k)
% 0x10  2^15 samples (32k)
% 0x20  2^16 samples (64k)
% 0x30  2^17 samples (128k)
% 0x40  2^18 samples (256k)
% 0x50  2^19 samples (512k)
% 0x60  2^20 samples (1M)
% 0x70  2^21 samples (2M)
% 0x80  2^22 samples (4M)
% 0x90  2^23 samples (8M)
% 0xA0  2^24 samples (16M)
% 0xB0  2^25 samples (32M)
% 0xC0  2^26 samples (64M)
% 0xD0  2^27 samples (128M)
% 0xE0  2^28 samples (256M)

FPGA_STATUS_REG         = 2;
% Bit 6 -    FWRFUL: The FIFO writing data to external DDR3 is full.
% Bit 5 -    FRDFUL: The FIFO reading data from external DDR3 is full.
% Bit 4 -    DDRPLL: The embedded PLL of the DDR controller is locked.
% Bit 3 -    DDRRDY: External DDR is ready to access.
% Bit 2 -    PLL0: The PLL accepting SYSCLK is locked. 
% Bit 1 -    PLL1: The PLL accepting DDCK is locked. 
% Bit 0 -    PLL2: The PLL accepting fifoclk is locked. 

FPGA_DAC_PD             = 3;
% Bit 0 (DACPD) = 0 - Turn OFF DAC
% Bit 0 (DACPD) = 1 - Turn ON DAC

register_dump = @(device) {
                            fprintf('LTC2000 Register Dump:\n');
                            fprintf('Register 1: 0x%02X\n', spiRead(device, 1));
                            fprintf('Register 2: 0x%02X\n', spiRead(device, 2));
                            fprintf('Register 3: 0x%02X\n', spiRead(device, 3));
                            fprintf('Register 4: 0x%02X\n', spiRead(device, 4));
                            fprintf('Register 5: 0x%02X\n', spiRead(device, 5));
                            fprintf('Register 6: 0x%02X\n', spiRead(device, 6));
                            fprintf('Register 7: 0x%02X\n', spiRead(device, 7));
                            fprintf('Register 8: 0x%02X\n', spiRead(device, 8));
                            fprintf('Register 9: 0x%02X\n', spiRead(device, 9));
                          };
                      
spiWrite = @(device, address, value) device.spiSendByteAtAddress(...
            bitor(address, SPI_WRITE), 1, value);
        
spiRead = @(device, address) device.spiReceiveByteAtAddress(...
            bitor(address, SPI_READ), 1);
      
