/*
LTC2309
12-bit, 8-channel SAR ADC

I2C DATA FORMAT (MSB First):
  
       Byte #1                                    Byte #2                       Byte #3                             Byte #4
                                                                         MSB                                 LSB
START  SA6 SA5 SA4 SA3 SA2 SA1 SA0 W SACK  C3 C2 C1 C0 A3 A2 A1 A0 SACK  D11 D10 D9  D8  D7  D6  D5 D4 SACK  D3 D2 D1 D0 X  X  X  X  SACK  STOP

SD   : Single/Differential Bit
OS   : ODD/Sign Bit
Sx   : Address Select Bit
COM  : CH7/COM Configuration Bit
UNI  : Unipolar/Bipolar Bit
SLP  : Sleep Mode Bit
Dx   : Data Bits
X    : Don't care 

DATA TYPES:
char  = 1 byte
int   = 2 bytes
long  = 4 bytes
float = 4 bytes 
  
REVISION HISTORY
$Revision: 719 $
$Date: 2012-10-26 14:22:35 -0700 (Fri, 26 Oct 2012) $
  
LICENSE  
Permission to freely use, copy, modify, and distribute this software for any 
purpose with or without fee is hereby granted, provided that the above 
copyright notice and this permission notice appear in all copies:
 
THIS SOFTWARE IS PROVIDED "AS IS" AND LTC DISCLAIMS ALL WARRANTIES
INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
EVENT SHALL LTC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM ANY USE OF SAME, INCLUDING
ANY LOCS OF USE OR DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTUOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR 
PERFORMANCE OF THIS SOFTWARE.

Copyright 2012 Linear Technology Corp. (LTC)
*/

#ifndef LTC2309_h
#define LTC2309_h

// Address Choices:
// To choose an address, comment out all options except the 
// configuration on the demo board.

                                      //  Address assignment
// LTC2309 I2C Address                 //  AD1       AD0
#define LTC2309_I2C_ADDRESS 0x10      //  LOW       LOW
// #define LTC2309_I2C_ADDRESS 0x12    //  LOW       Float
// #define LTC2309_I2C_ADDRESS 0x14    //  LOW       HIGH
// #define LTC2309_I2C_ADDRESS 0x16    //  Float     HIGH
// #define LTC2309_I2C_ADDRESS 0x30    //  Float     Float
// #define LTC2309_I2C_ADDRESS 0x32    //  Float     LOW
// #define LTC2309_I2C_ADDRESS 0x34    //  HIGH      LOW
// #define LTC2309_I2C_ADDRESS 0x36    //  HIGH      Float
// #define LTC2309_I2C_ADDRESS 0x28    //  High      HIGH


// Single-Ended Channel Configuration
#define LTC2309_CH0                0x88
#define LTC2309_CH1                0xC8
#define LTC2309_CH2                0x98
#define LTC2309_CH3                0xD8
#define LTC2309_CH4                0xA8
#define LTC2309_CH5                0xE8
#define LTC2309_CH6                0xB8
#define LTC2309_CH7                0xF8

// Differential Channel Configuration
#define LTC2309_P0_N1              0x00
#define LTC2309_P1_N0              0x40

#define LTC2309_P2_N3              0x10
#define LTC2309_P3_N2              0x50

#define LTC2309_P4_N5              0x20
#define LTC2309_P5_N4              0x60

#define LTC2309_P6_N7              0x30
#define LTC2309_P7_N6              0x70


//Command
#define LTC2309_SLEEP_MODE         0x04
#define LTC2309_EXIT_SLEEP_MODE    0x00
#define LTC2309_UNIPOLAR_MODE      0x08


// Commands
// Construct a channel / uni/bipolar int by bitwise ORing one choice from the channel configuration
// and one choice from the command. 

// Example - read channel 3 single-ended 
// adc_command = LTC2309_CH3 | LTC2309_UNIPOLAR_MODE;

// Example - read channels 5 and 4 with 4 as positive polarity and in bipolar mode.
// adc_command = LTC2309_P4_N5;

//Calibration Variables
float LTC2309_lsb = 1.0002442E-03;
float LTC2309_offset_code=0;

unsigned char LTC2309_read(unsigned char i2c_address, unsigned char adc_command, int& code)
//Reads 12 bits
{
    unsigned char ack = 0;
    union {unsigned char b[2]; long w;} data;    // combines bytes
    i2c_start();                                // write an I2C start bit
    ack = i2c_write(i2c_address & 0xFE);        // write the I2C 8 bit address and !W bit in the LSB position
    if (!ack)
    {
        ack = i2c_write(adc_command);           // write the command byte
        i2c_start();
        ack = i2c_write(i2c_address | 0x01);      // write the I2C 8 bit address and !R bit in the LSB position
        if(!ack)
        {
            data.b[1]=i2c_read(0);              // reads MSB byte with ACK
            data.b[0]=i2c_read(1);              // reads LSB byte with Nack
        }
    }
    i2c_stop();                                 // write an I2C stop bit
    data.w >>= 4;                               // shifts data 4 bits to the right
    code = data.w;
    return(ack);
}

float LTC2309_unipolar_voltage(long adc_code)
// Calculates the LTC2309 input unipolar voltage.
{
    float adc_voltage;
    adc_voltage=((float)adc_code-LTC2309_offset_code)*LTC2309_lsb;
    return(adc_voltage);
}
float LTC2309_bipolar_voltage(long adc_code)
// Calculates the LTC2309 input bipolar voltage
{
    float adc_voltage, sign = 1.0;
    if(adc_code>>11)
    {
        adc_code = (adc_code ^ 0xFFF)+1;       // converts two's complement
        sign = -1;
    }
    adc_voltage=((float)adc_code-LTC2309_offset_code)*LTC2309_lsb*sign;
    return(adc_voltage);
}

void LTC2309_cal_voltage(long zero_code, long fs_code, float fs_voltage)
// Calibrate the lsb
{
    LTC2309_offset_code=(float)zero_code;
    LTC2309_lsb=fs_voltage/((float)fs_code-LTC2309_offset_code);
}
#endif
