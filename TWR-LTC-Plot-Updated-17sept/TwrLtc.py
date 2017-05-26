#-------------------------------------------------------------------------------
# Name:        TwrLtc.py
# Purpose:     This module processes the information related to TwrLTC board
#
# Author:      Navin
#
# Created:     14/07/2011
# Copyright:   (c)MDN
# Licence:     MDN licence
#-------------------------------------------------------------------------------
#!/usr/bin/env python


class TwrLtc:
    """ This class models the tower k60n512-LTC adcdac kit. This class has
    methods that perfomr the conversion between the digital value and the
    voltages for the various ICs mounted on the TWR """

    def __init__(self):
        self.ltc2498_ref_vltg= 5.00
        self.ltc2600_ref_vltg= 5.00
        self.ltc1859_ref_vltg= 5.00
        self.ltc2704_ref_vltg= 5.00

    def ltc2600_data(self, value):
        """ This function calculates appropriate value for outputing analog
        voltage required by the ltc2600. This method excepts val to be of type
        string. The string holds the analog value to be output. Say, 1.55.
        Note:  This function returns hex representation of the digital value
        required to output the desired analog volatge """

        if type(value) != type(""):
            raise ValueError, "ltc2600_data: This method requires a string type\
                              parameter  "

        try:
            vltg = float(value)
        except ValueError:
            raise ValueError, "ltc2600_data: string represnting floating point \
                               was expected "
        quant = 2**16 - 1
        digi_rep = (vltg* quant)/self.ltc2600_ref_vltg # 16-bit DAC

        hex_rep = "%x" %(digi_rep)
        hex_rep = hex_rep[:4]      # only first four chars
        return hex_rep.upper()

    def ltc2704_data(self, value):
	""" This function calculates appropriate value for outputing analog
        voltage required by the ltc2704. This method excepts val to be of type
        string. The string holds the analog value to be output. Say, 1.55.
        Note:  This function returns hex representation of the digital value
        required to output the desired analog volatge """
        if type(value)!= type(""):
            raise ValueError, "ltc2704_data: This method requires a string type\
                              parameter  "

        try:
            vltg = float(value)
        except ValueError:
            raise ValueError, "ltc2704_data: string represnting floating point \
                               was expected "
        quant = 2**16 - 1
        digi_rep = (vltg* quant)/self.ltc2704_ref_vltg # 16-bit DAC

        hex_rep = "%x" %(digi_rep)
        hex_rep = hex_rep[:4]      # only first four chars
        return hex_rep.upper()



    def ltc2498_data(self, value):
        """ This method calculates the analog volatge measured by the ltc2498
        and returns the volatge """
        try:
            value = int(value)
        except ValueError:
            raise ValueError, "ltc249_data: was expecting a string representing an integer"
        val = (((((value - 536870912.0)/536870912.0)*self.ltc2498_ref_vltg)) *100000.0)/100000.0
        return val

    def ltc1859_data(self, value):
        """ This method calculates the analog volatge measured by the ltc2498
        and returns the volatge """
        try:
            value = int(value)
        except ValueError:
            raise ValueError, "ltc1859data: was expecting a string representing an integer"
        val = ((((value/65535.0)*self.ltc1859_ref_vltg)) *100000.0)/100000.0
        return val

    def ltc2498_set_ref(self, vltg):
        """ This method sets the reference volatge for ltc2598 """
        if type(vltg) != type(1.23):
            raise ValueError, "ltc2498_set_ref: A floating point number was expected "
        self.ltc2498_ref_vltg = vltg

    def ltc2600_set_ref(self, vltg):
        """ This method sets the reference volatge for the ltc2600 """
        if type(vltg) != type(1.23):
            raise ValueError, "ltc2600_set_ref: A floating point number was expected "
        self.ltc2600_ref_vltg = vltg

    def ltc2704_set_ref(self, vltg):
        """ This method sets the reference volatge for ltc2704 """
        if type(vltg) != type(1.23):
            raise ValueError, "ltc2704_set_ref: A floating point number was expected "
        self.ltc2704_ref_vltg = vltg

    def ltc1859_set_ref(self, vltg):
        """ This method sets the reference volatge for the ltc1859 """
        if type(vltg) != type(1.23):
            raise ValueError, "ltc1859_set_ref: A floating point number was expected "
        self.ltc1859_ref_vltg = vltg

def test():
    twr1 = TwrLtc()
    import random

    for i in range(10):
        ran = random.random()*5
        x = str(ran)
        print " %s converted is %s " %(x, twr1.ltc2600_data(x))


if __name__ == '__main__':
    test()




