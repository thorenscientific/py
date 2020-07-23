#!/usr/bin/env python 

#    Created by: Noe Quintero
#    E-mail: nquintero@linear.com
#
#    REVISION HISTORY
#    $Revision: 2589 $
#    $Date: 2014-07-07 10:25:53 -0700 (Mon, 07 Jul 2014) $
#
#    Copyright (c) 2013, Linear Technology Corp.(LTC)
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#    The views and conclusions contained in the software and documentation are those
#    of the authors and should not be interpreted as representing official policies,
#    either expressed or implied, of Linear Technology Corp.

# Import libraries
from ltc_spi_avalon import *

# ************************************************
# Two-To-One MUX
# ************************************************

# Description:	The component is controlled by a host or main through the 
#                CSR subordinate port to control which streaming data input will be 
#                routed to the streaming data output.

# Register map:

#           Access Type                  Bits
#                        31..24   23..16    15..8          7..0
# Address 0    w           N/A      N/A   clear pipeline  input select
# Address 4    r           N/A      N/A   pending data    selected input

# Each control and status value is a single bit aligned to the lowest bit of 
# the byte lane (bits 0 or 8). Input select == 0 --> input A is selected 
# otherwise input B is selected.


class Mux:
    # Registers with byte addressing
    INPUT_SELECT_REG                   = 0x00
    CLEAR_PIPLINE_REG                  = 0x01
    SELECTED_INPUT_REG                 = 0x04
    PENDING_DATA_REG                   = 0x05
        
    def __init__(self):
        pass

    # Reads the pending data bit
    # Returns  0 = no data in the pipeline, 1 = data in the pipeline
    @staticmethod    
    def pending_data(dc590, base):
        data = transaction_read(
            dc590,
            base + Mux.PENDING_DATA_REG,
            1)
        return data[0]
    
    # Selects the input of the MUX
    # returns 0 = success, -1 = fail
    @staticmethod    
    def input_select(dc590, base, select):
        pass_fail = 0
        data_out = []
        
        # Check for data in the pipeline
        data_in = Mux.pending_data(dc590, base)
        
        if (data_in == 0):
            # if no data was present, change the input
            data_out.append(select)
            transaction_write(
                dc590, 
                base + Mux.INPUT_SELECT_REG,
                1,
                data_out)
        else:
            # There was data in the pipeline, do not change the input
            pass_fail = -1
        return pass_fail
    
    # Clears the MUX's pipeline 
    @staticmethod    
    def clear_pipeline(dc590, base):
        transaction_write(
            dc590, 
            base + Mux.CLEAR_PIPLINE_REG,
            1,
            [1])
    
    # Reads which input is selected for the MUX
    # Returns the selected channel
    @staticmethod    
    def selected_input(dc590, base):
        data = transaction_read(
            dc590, 
            base + Mux.SELECTED_INPUT_REG,
            1)
        return data[0]


# ************************************************
# One-To-Two DEMUX
# ************************************************

# Description:	The component is controlled by a host or main through the CSR
#               subordinate port to control which streaming data output the input
#               streaming data will be routed to.

# Register map:

#             Access Type    Bits
#                           31..24  23..16  15..8          7..0
# Address 0   w              N/A    N/A     clear pipeline output select
# Address 4   r              N/A    N/A     pending data   selected output

# Each control and status value is a single bit aligned to the lowest bit of 
# the byte lane (bits 0 or 8).
# Output select == 0 --> output A is selected otherwise output B is selected.
# Pending data has two bits since there are two outputs. Bit 8 represents the A
# output containing pending data. Bit 9 represents the B output containing 
# pending data.

class Demux:
    
    # Registers with byte addressing
    OUTPUT_SELECT_REG                     = 0x00
    CLEAR_PIPELINE_REG                    = 0x01
    SELECTED_OUTPUT_REG                   = 0x04
    PENDING_DATA_REG                      = 0x05

    def __init__(self):
        pass
    
    # Reads the pending data bit
    # Returns  0 = no data in the pipeline, 1 = data in the pipeline
    @staticmethod    
    def pending_data(dc590, base):
        data = transaction_read(
            dc590, 
            base + Demux.PENDING_DATA_REG,
            1)
        return data[0]
    
    # Selects the output of the DEMUX
    # returns 0 = success, -1 = fail
    @staticmethod    
    def output_select(dc590, base, select):
        pass_fail = 0
        data_out = []
        
        # Check for data in the pipeline
        data_in = Demux.pending_data(dc590, base)
        
        if (data_in == 0):
            # if no data was present, change the output
            data_out.append(select)
            transaction_write(
                dc590, 
                base + Demux.OUTPUT_SELECT_REG,
                1, 
                data_out)
        else:
            # There was data in the pipeline, do not change the input
            pass_fail = -1
        return pass_fail
    
    # Clears the DEMUX's pipeline
    @staticmethod
    def clear_pipeline(dc590, base):
        transaction_write(
            dc590, 
            base + Demux.CLEAR_PIPELINE_REG,
            1, 
            [1])
    
    # Reads which output is selected for the DEMUX
    # Returns the selected channel
    @staticmethod    
    def selected_output(dc590, base):
        data = transaction_read(
            dc590, 
            base + Demux.SELECTED_OUTPUT_REG,
            1)
        return data[0]

# ************************************************
# Custom Pattern Checker
# ************************************************

# Description:  This component is programmed via a host or main through the 
#               pattern subordinate port to program the internal test memory.  When 
#               the host writes to the start bit of the CSR subordinate port the 
#               component will begin to send the contents from the internal 
#               memory to the data streaming port. You should use the custom 
#               pattern generator component with this component.

# Register map:

# Address | Access Type |  Bits                                          |
#         |             |  31..24   |   23..16   |   15..8   |   7..0    |
#   0     |    r/w      |               Payload Length                   |
#   4     |    r/w      |  Pattern Position               Pattern Length |
#   8     |    r/w      | Run   Stop on Failure  Infinite Payload Length |
#  12     |   r/clr     |                               Failure Detected |

# Address 0  --> Bits 31:0 are used store the payload length as well as read it
#                back while the checker core is operating.  This field should 
#                only be written to while the checker is stopped.
# Address 4  --> Bits 15:0 is used to store pattern length, bits 31:16 used to 
#                store a new position in the pattern. The position will update 
#                as the checker is operating. These fields should only be 
#                written to while the checker core is stopped.
# Address 8  --> Bit 0 is used tell the checker to ignore the payload length 
#                field and generate the pattern until stopped.  Bit 8 is used 
#                to stop the checker when a failure is detected and bit 24 is 
#                used to start the checker core so that it begins receiving 
#                data. The run field must be accessed at the same time as the 
#                other two bits or later.
# Address 12 --> Bit 0 is used to read back the failure status as well as clear
#                the failure bit

class Checker:
    
    # Registers with byte addressing
    PAYLOAD_LENGTH_REG                          = 0x0
    PATTERN_LENGTH_REG                          = 0x4
    PATTERN_POSITION_REG                        = 0x6
    INFINITE_PAYLOAD_LENGTH_REG                 = 0x8
    STOP_ON_FAILURE_REG                         = 0x9
    RUN_REG                                     = 0xB
    FAILURE_DETECTED_REG                        = 0xC
        
    def __init__(self):
        pass
    
    # Register write functions
    @staticmethod    
    def set_payload_length (dc590, base, length):
        data_out = []
        for x in range(0,4):
            data_out.append(int((length & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(dc590, base + Checker.PAYLOAD_LENGTH_REG,4, data_out)
    
    @staticmethod    
    def set_pattern_length (dc590, base, length):
        data_out = []
        for x in range(0,2):
            data_out.append(int((length & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(
            dc590, 
            base + Checker.PATTERN_LENGTH_REG, 
            2, 
            data_out)
    @staticmethod
    def set_pattern_position (dc590, base, position):
        data_out = []
        for x in range(0,2):
            data_out.append(int((position & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(
        dc590, 
        base + Checker.PATTERN_POSITION_REG,
        2, 
        data_out)
    
    @staticmethod    
    def enable_infinite_payload_length (dc590, base):
        transaction_write(
            dc590, 
            base + Checker.INFINITE_PAYLOAD_LENGTH_REG, 
            1, 
            [1])
    
    @staticmethod
    def disable_infinite_payload_length (dc590, base):
        transaction_write(
            dc590, 
            base + Checker.INFINITE_PAYLOAD_LENGTH_REG,
            1, 
            [0])
    
    @staticmethod
    def enable_stop_on_failure (dc590, base):
        transaction_write(
            dc590, 
            base + Checker.STOP_ON_FAILURE_REG, 
            1, 
            [1])
    
    @staticmethod    
    def disable_stop_on_failure (dc590, base):
        transaction_write(
        dc590, 
        base + Checker.STOP_ON_FAILURE_REG,
        1, 
        [0])
    
    @staticmethod
    def enable_start (dc590, base):
        transaction_write(
            dc590, 
            base + Checker.RUN_REG,
            1, 
            [1])
    
    @staticmethod
    def disable_start (dc590, base):
        transaction_write(
            dc590, 
            base + Checker.RUN_REG,
            1, 
            [0])
    
    # Register read functions
    @staticmethod    
    def read_payload_length (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Checker.PAYLOAD_LENGTH_REG, 
            4)
        return data_in[0] + (data_in[1]<<8) + (data_in[2]<<16) + (data_in[3]<<24)
        
    # BUG: Does Not work!
    @staticmethod
    def read_pattern_length (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Checker.PATTERN_LENGTH_REG, 
            2)
        return data_in[0] + (data_in[1]<<8)

    # BUG: Does Not work!
    @staticmethod
    def read_pattern_position (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Checker.PATTERN_POSITION_REG,
            2)    
        return data_in[0] + (data_in[1]<<8)
    @staticmethod
    def read_infinite_payload_length (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Checker.INFINITE_PAYLOAD_LENGTH_REG,
            1)
        return data_in[0]
    
    # BUG: Does Not work!
    @staticmethod    
    def read_stop_on_failure (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Checker.STOP_ON_FAILURE_REG,
            1)
        return data_in[0]
    
    @staticmethod
    def read_start (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Checker.RUN_REG,
            1)
        return data_in[0]
    
    @staticmethod
    def read_failure_detected (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Checker.FAILURE_DETECTED_REG,
            1)
        return data_in[0]
    
    # Register clear function
    @staticmethod    
    def clear_failure (dc590, base):
        transaction_write(
            dc590, 
            base + Checker.FAILURE_DETECTED_REG, 
            1,
            [1])

    
# ************************************************
# Custom Pattern Generator
# ************************************************

# Description:  
# This component is programmed via a host or main through the pattern subordinate 
# port to program the internal test memory. When the hos writes to the start 
# bit of the CSR subordinate port the component will begin to send the contents from 
# the internal memory to the data streaming port. You should use the custom 
# pattern checker component with this component.

# Register map:


# Address | Access Type | Bit
#         |             |  31..24  |  23..16  |  15..8  |  7..0  |
#   0     |     r/w     |    Payload Length                      |
#   4     |     r/w     | Pattern Position      Pattern Length   |
#   8     |     r/w     |      Run       Infinite Payload Length |
#   12    |     N/A     |           N/A                          |


# Address 0  --> Bits 31:0 are used store the payload length as well as read it
#                back while the checker core is operating.  This field should 
#                only be written to while the checker is stopped.
# Address 4  --> Bits 15:0 is used to store pattern length, bits 31:16 used to 
#                store a new position in the pattern.  The position will update
#                as the checker is operating. These fields should only be 
#                written to while the checker core is stopped.
# Address 8  --> Bit 0 is used tell the checker to ignore the payload length 
#                field and generate the pattern until stopped. The run field 
#                must be accessed at the same time as the other bit or later.
#Address 12 --> <reserved>

class Generator:
    
    # 32-bit registers with byte addressing
    PAYLOAD_LENGTH_REG                          = 0x0
    PATTERN_LENGTH_REG                          = 0x4 
    PATTERN_POSITION_REG                        = 0x6    
    INFINITE_PAYLOAD_LENGTH_REG                 = 0x8
    RUN_REG                                     = 0xB
    
    def __init__(self):
        pass
    
    # Register write functions
    @staticmethod    
    def set_payload_length (dc590, base, length):
        data_out = []
        for x in range(0,4):
            data_out.append(int((length & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(
            dc590, 
            base + Generator.PAYLOAD_LENGTH_REG, 
            4, 
            data_out)
    
    @staticmethod
    def set_pattern_length (dc590, base, length):
        data_out = []
        for x in range(0,2):
            data_out.append(int((length & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(
            dc590, 
            base + Generator.PATTERN_LENGTH_REG, 
            2, 
            data_out)
    
    @staticmethod
    def set_pattern_position (dc590, base, position):
        data_out = []
        for x in range(0,2):
            data_out.append(int((position & (0xFF<<(x*8)))>>(x*8)))
        
        transaction_write(
            dc590, 
            base + Generator.PATTERN_POSITION_REG,
            2, 
            data_out)
    
    @staticmethod
    def enable_infinite_payload_length (dc590, base):
        transaction_write(
            dc590, 
            base + Generator.INFINITE_PAYLOAD_LENGTH_REG,
            1, 
            [1])
    
    @staticmethod
    def disable_infinite_payload_length (dc590, base):
        transaction_write(
            dc590, 
            base + Generator.INFINITE_PAYLOAD_LENGTH_REG,
            1, 
            [0])
    
    @staticmethod    
    def enable_start (dc590, base):
        transaction_write(
            dc590, 
            base + Generator.RUN_REG, 
            1, 
            [1])
    
    @staticmethod
    def disable_start (dc590, base):
        transaction_write(
            dc590, 
            base + Generator.RUN_REG,  
            1, 
            [0])
    
    # Register read functions
    @staticmethod    
    def read_payload_length (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Generator.PAYLOAD_LENGTH_REG, 
            4)
        return data_in[0] + (data_in[1]<<8) + (data_in[2]<<16) + (data_in[3]<<24)
    
    @staticmethod    
    def read_pattern_length (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Generator.PATTERN_LENGTH_REG, 
            2)
        return (data_in[0] + (data_in[1]<<8))
    
    @staticmethod        
    def read_pattern_position (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Generator.PATTERN_POSITION_REG, 
            2)
        return (data_in[0] + (data_in[1]<<8))
        
    @staticmethod
    def read_infinite_payload_length (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Generator.INFINITE_PAYLOAD_LENGTH_REG, 
            1)
        return data_in[0] 
    
    @staticmethod
    def read_start (dc590, base):
        data_in = transaction_read(
            dc590, 
            base + Generator.RUN_REG, 
            1)
        print data_in
        return data_in[0]


# ************************************************
# Ram Test Controller
# ************************************************

#Register map:

# Address | Access Type | Bits                                   |
#         |             |  31..24  |  23..16  |  15..8  |  7..0  |
#   0     |    r/w      |        Base Address[31..0]             |
#   4     |    r/w      |        Base Address[63..32]            |
#   8     |    r/w      |        Transfer Length[31..0]          |
#   12    |    r/w      | Block Trail[7..0]    Block Size[23..0] |
#   16    |    r/w      | Start            Concurrent R/W Enable |
#   20    |    N/A      |                 N/A                    |
#   24    |    r/w      |                Timer Resolution[15..0] |
#   28    |    r/w      |            Timer[31..0]                |


# Address 0  --> Lower 32 bits of the base address
# Address 4  --> Upper 32 bits of the base address (Note this will not be 
#                addressable in SOPC Builder)
# Address 8  --> Transfer length register
# Address 12 --> Bits 23-0 are used to specify the transfer block size. The 
#                block size (in bytes) is used to determine how large of block 
#                of memory should be tested at any given time. If 'concurrent 
#                r/w enable' is set to 0 then the block size represents how much
#                data will be written before a read verification cycle starts.  
#                Bits 31-24 are used to specify the block trail. The block trail
#                represents how many blocks the read main should trail the 
#                write main by. A block trail of 0 means that the block is 
#                written out and read back immediately. A block train of 1 means
#                that two blocks will be written followed by reading the first block.
# Address 16 --> Bit 0 is used to enable concurrent read and write block 
#                operations. When disabled the read main remains idle while 
#                the write main operates. When enabled the read and write 
#                mains can operate concurrently presenting a mix of read and
#                write accesses to the memory. Bit 24 is used to start the 
#                memory test mains and will remain enabled until the last 
#                read data returns to the read main.
# Address 20 --> N/A
# Address 24 --> Timer resolution in terms of system clock cycles. If the 
#                system clock speed is 100MHz (T=10ns) then setting the 
#                resolution to 100 ticks will result in the timer having a 1us 
#                timer resolution. By default the timer resolution is 10 ticks.
#                The timer resolution is used to generate a free running slower
#                clock which operates at all times.  As a result this clock 
#                divider value must be between 2 and 65535.
# Address 28 --> Timer with write capabilities. The timer counts the number of 
#                times the free running timer reaches the terminal value while 
#                the start bit is set. To take multiple measurments you can 
#                either write a 0 to the timer register before enabling the 
#                test to get a measurement for each test or run multiple tests 
#                and reading the timer value at the end of the test. While the 
#                test is not operating (start == 0) the timer will stop and 
#                hold it's previous value.

class RamTestController:
    
    # Registers with byte address
    LOW_BASE_ADDRESS_REG                    = 0x0 
    HIGH_BASE_ADDRESS_REG                   = 0x4
    TRANSFER_LENGTH_REG                     = 0x8
    BLOCK_SIZE_REG                          = 0xC
    BLOCK_TRAIL_REG                         = 0xf
    CONCURRENT_ENABLE_REG                   = 0x10
    START_REG                               = 0x13
    TIMER_RES_REG                           = 0x18
    TIMER_REG                               = 0x1C
    
    def __init__(self):
        pass
    
    # Register write functions
    @staticmethod
    def set_base_address (dc590, csr_base, ram_base):
        data_out = []
        for x in range(0,8):
            data_out.append(int((ram_base & (0xFF<<(x*8)))>>(x*8)))
        
        transaction_write(
            dc590, 
            csr_base + RamTestController.LOW_BASE_ADDRESS_REG, 
            8, 
            data_out)
        
    # Returns 0 when a valid transfer length is passed in otherwise 1 will be returned
    @staticmethod
    def set_transfer_length (dc590, csr_base, length):
        fail = 0
        # default block size in hardware is 32 so might as well fall back to this    
        if length < 32:    
            length = 32
            fail = 1
        data_out = []
        for x in range(0,4):
            data_out.append(int((length & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(
            dc590, 
            csr_base + RamTestController.TRANSFER_LENGTH_REG, 
            4, 
            data_out)
        return fail 
    
    # Returns 0 when a valid block size is passed in otherwise 1 will be returned
    @staticmethod
    def set_block_size (dc590, csr_base, block_size):
        fail = 0
        block_size = block_size & 0xFFFFFF    
        # default that the hardware uses    
        if block_size < 32:    
            block_size = 32
            fail = 1
        data_out = []
        for x in range(0,3):
            data_out.append(int((block_size & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(
            dc590, 
            csr_base + RamTestController.BLOCK_SIZE_REG, 
            3, 
            data_out)
        return fail 
    
    # Returns 0 when a valid trail distance is passed in otherwise 1 will be returned
    @staticmethod
    def set_block_trail_distance (dc590, csr_base, trail_distance):
        fail = 0
        data_out = []
        # default that the hardware uses
        if trail_distance == 0:
            trail_distance = 1    
            fail = 1
        data_out.append(trail_distance)
        transaction_write(
            dc590, 
            csr_base + RamTestController.BLOCK_TRAIL_REG,
            1,
            data_out)
        return fail   
    
    @staticmethod
    def enable_concurrent_accesses (dc590, csr_base):
        transaction_write(
            dc590, 
            csr_base + RamTestController.CONCURRENT_ENABLE_REG,
            1,
            [1])
    
    @staticmethod
    def disable_concurrent_accesses (dc590, csr_base):
        transaction_write(
            dc590, 
            csr_base + RamTestController.CONCURRENT_ENABLE_REG,
            1,
            [0])
    
    @staticmethod
    def enable_start (dc590, csr_base):
        transaction_write(
            dc590, 
            csr_base + RamTestController.START_REG,
            1,
            [1])
    @staticmethod
    def disable_start (dc590, csr_base):
        transaction_write(
            dc590, 
            csr_base + RamTestController.START_REG,
            1,
            [0])
    
    # Returns 0 when a valid timer resolution is passed in otherwise 1 will be returned
    @staticmethod
    def set_timer_resolution (dc590, csr_base, resolution):
        fail = 0
        # the resolution acts as a clock divider so it must be 2 or greater    
        # default that the hardware uses    
        if resolution < 2:
            resolution = 10
            fail = 1
        data_out = []
        for x in range(0,2):
            data_out.append(int((resolution & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(
            dc590, 
            csr_base + RamTestController.TIMER_RES_REG,
            2,
            data_out)
        return fail
    
    # Use this to reset the timer by passing in timer = 0
    @staticmethod
    def set_timer (dc590, csr_base, timer):
        data_out = []
        for x in range(0,4):
            data_out.append(int((timer & (0xFF<<(x*8)))>>(x*8)))
        transaction_write(
            dc590, 
            csr_base + RamTestController.TIMER_REG,
            4,
            data_out)
    
    # Register read functions
    @staticmethod
    def read_base_address (dc590, csr_base):
        data_in = transaction_read(
            dc590, 
            csr_base + RamTestController.LOW_BASE_ADDRESS_REG, 
            8)
        return (data_in[0] + (data_in[1]<<8) + (data_in[2]<<16) + (data_in[3]<<24) + 
            (data_in[4]<<32) + (data_in[5]<<40) + (data_in[6]<<48) + (data_in[7]<<56))
    
    @staticmethod
    def read_transfer_length (dc590, csr_base):
        data_in = transaction_read(
            dc590, 
            csr_base + RamTestController.TRANSFER_LENGTH_REG, 
            4)
        return (data_in[0]) + (data_in[1]<<8) + (data_in[2]<<16) + (data_in[3]<<24)
    
    @staticmethod        
    def read_block_size (dc590, csr_base):
        data_in = transaction_read(
            dc590, 
            csr_base + RamTestController.BLOCK_SIZE_REG, 
            3)
        return data_in[0] + (data_in[1]<<8) + (data_in[2]<<16)
    
    @staticmethod
    def read_block_trail_distance (dc590, csr_base):
        data_in = transaction_read(
            dc590, 
            csr_base + RamTestController.BLOCK_TRAIL_REG, 
            1)
        return data_in[0]
    
    @staticmethod
    def read_concurrent_accesses (dc590, csr_base):
        data_in = transaction_read(
            dc590, 
            csr_base + RamTestController.CONCURRENT_ENABLE_REG, 
            1)
        return data_in[0]
    
    @staticmethod
    def read_start (dc590, csr_base):
        data_in = transaction_read(
            dc590, 
            csr_base + RamTestController.START_REG, 
            1)
        return data_in[0]
    
    @staticmethod
    def read_timer_resolution (dc590, csr_base):
        data_in = transaction_read(
            dc590, 
            csr_base + RamTestController.TIMER_RES_REG, 
            2)
        return data_in[0] + (data_in[1]<<8) 
    
    @staticmethod
    def read_timer (dc590, csr_base):
        data_in = transaction_read(
            dc590, 
            csr_base + RamTestController.TIMER_REG, 
            4)
        return data_in[0] + (data_in[1]<<8) + (data_in[2]<<16) + (data_in[3]<<24) 


# ************************************************
# Function Tests
# ************************************************

if __name__ == "__main__":
    
    try:
        dc590 = DC590() # Look for the DC590
        
        print 'Test MUX Functions'        
        print Mux.input_select(dc590, 0x440, 1) # Set to Channel 1
        print 'Mux Channel: ' + hex(Mux.selected_input(dc590, 0x440))
        Mux.clear_pipeline(dc590, 0x440)
        print Mux.pending_data(dc590, 0x440)
        
        print 'Test DEMUX Functions'
        print Demux.output_select(dc590, 0x1400, 1) # Set to Channel 1
        print 'Demux Channel : ' + hex(Demux.selected_output(dc590, 0x1400))
        Demux.clear_pipeline(dc590, 0x1400)
        print Demux.pending_data(dc590, 0x1400)
        
        print 'Test Checker Functions'
        Checker.set_payload_length(dc590, 0x400, 0xAAFFBB11)
        print hex(Checker.read_payload_length(dc590, 0x400)) 
        Checker.set_pattern_length(dc590, 0x400, 0xFF01)
        print hex(Checker.read_pattern_length(dc590, 0x400))
        Checker.set_pattern_position(dc590, 0x400, 0xAA02)
        print hex(Checker.read_pattern_position(dc590, 0x400))
        Checker.disable_infinite_payload_length(dc590, 0x400)        
        Checker.enable_infinite_payload_length(dc590, 0x400)
        print Checker.read_infinite_payload_length(dc590, 0x400)
        Checker.disable_stop_on_failure(dc590, 0x400)
        Checker.enable_stop_on_failure(dc590, 0x400)
        print Checker.read_stop_on_failure(dc590, 0x400)
        Checker.disable_start(dc590, 0x400)
        Checker.enable_start(dc590, 0x400)
        print Checker.read_start(dc590, 0x400)
        Checker.clear_failure(dc590, 0x400)
        print Checker.read_failure_detected(dc590, 0x400)
        
        print 'Test Generator Functions'
        Generator.set_payload_length(dc590, 0x400, 0xAAFFBB11)
        print hex(Generator.read_payload_length(dc590, 0x400)) 
        Generator.set_pattern_length(dc590, 0x400, 0xFF01)
        print hex(Generator.read_pattern_length(dc590, 0x400))
        Generator.set_pattern_position(dc590, 0x400, 0xAA02)
        print hex(Generator.read_pattern_position(dc590, 0x400))
        Generator.disable_infinite_payload_length(dc590, 0x400)        
        Generator.enable_infinite_payload_length(dc590, 0x400)
        print Generator.read_infinite_payload_length(dc590, 0x400)
        Generator.disable_start(dc590, 0x400)
        Generator.enable_start(dc590, 0x400)
        print Generator.read_start(dc590, 0x400)
        
        print 'Test RAM Test Controller Functions'
        RamTestController.set_base_address(dc590, 0x800, 0x010203)
        print hex(RamTestController.read_base_address(dc590, 0x800))
        print RamTestController.set_transfer_length(dc590, 0x800, 32)
        print RamTestController.read_transfer_length(dc590, 0x800)
        print RamTestController.set_block_size(dc590, 0x800, 32)
        print RamTestController.read_block_size(dc590, 0x800)
        print RamTestController.set_block_trail_distance(dc590, 0x800,0xFF)
        print hex(RamTestController.read_block_trail_distance(dc590, 0x800))
        RamTestController.disable_concurrent_accesses(dc590, 0x800)
        #RamTestController.enable_concurrent_accesses(dc590, 0x800)
        print RamTestController.read_concurrent_accesses(dc590, 0x800)
        RamTestController.disable_start(dc590, 0x800)
        RamTestController.enable_start(dc590, 0x800)
        print RamTestController.read_start(dc590, 0x800)
        print RamTestController.set_timer_resolution(dc590, 0x800, 2)
        print RamTestController.read_timer_resolution(dc590, 0x800)
        RamTestController.set_timer(dc590, 0x800, 0xFF)
        print hex(RamTestController.read_timer(dc590, 0x800))
        
    finally:
        dc590.close()
    print "Test Complete"