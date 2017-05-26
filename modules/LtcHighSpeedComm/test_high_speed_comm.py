# -*- coding: utf-8 -*-
"""
Created on Wed May 13 10:43:58 2015

@author: jeremy_s
"""

import ltc_high_speed_comm as lths
    
device_info = None
for info in lths.list_devices():
    # if you know the serial number you want, you could check that here
    if info.get_description() == "LTC2000 Demoboard":
        # you could use a with statement like the one below to open the
        # device and query it to make sure it is the one you want here
        device_info = info
        break
if device_info is None:
    raise Exception("could not find compatible device")
    
    
serial_number = device_info.get_serial_number()
print serial_number

# open and use the device
with lths.Lths(device_info) as device:
    device.set_bit_mode(lths.MODE_MPSSE)
    device.gpio_write_high_byte(0xFF)