#-------------------------------------------------------------------------------
# Name:        PIDRecipe
# Purpose:
#
# Author:      elbar
#
# Created:     12/10/2012
# Copyright:   (c) elbar 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import logging

#load logger
logger = logging.getLogger("PIDTuneLog")

# Constants
#-------------------------------------------------------------------------------
P_CONTROL = 0
PI_CONTROL = 1
PID_CONTROL = 2
PID_CONTROL_SMALL_OVERSHOOT = 3
PID_CONTROL_NO_OVERSHOOT = 4

PID_METHODS = [ 'Ziegler-Nichols',
                'Cohen-Coon',
                'ITAE load change',
                'ITAE set point change',
                'Direct synthesis',
                'IMC']

PID_METHODS_TYPES = [ [0, 1, 2],
                      [0, 1, 2],
                      [1, 2],
                      [1, 2],
                      [1],
                      [2] ]

PID_TYPES = ['P', 'PI', 'PID', 'PID small overshoot', 'PID no overshoot']

#-------------------------------------------------------------------------------
def ZN_ultimate(control, Kcu, wu):
#Ziegler-Nichols Ultimate-Gain Method
#Kcu =  critical (ultimate) gain
#wu  =  ultimate frequency in radian/time unit
#Pu  =  ultimate period in time unit

    logger.info("ZN Ultimate-Gain Method : Control Type = {}".format(PID_TYPES[control]))

    Pu= 2 * 3.1415 / wu

    if (control == P_CONTROL):
        Kc = 0.5 * Kcu
        return Kc, 0.0, 0.0
    elif (control == PI_CONTROL):
        Kc = 0.455 * Kcu
        taui = 0.833 * Pu
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        Kc = 0.588 * Kcu
        taui = 0.5 * Pu
        taud = 0.125 * Pu
        return Kc, taui, taud
    elif (control == PID_CONTROL_SMALL_OVERSHOOT):
        Kc = 0.333 * Kcu
        taui = 0.5 * Pu
        taud = 0.5 * Pu
        return Kc, taui, taud
    elif (control == PID_CONTROL_NO_OVERSHOOT):
        Kc = 0.2 * Kcu
        taui = 0.5 * Pu
        taud = 0.333 * Pu
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def ZN(control, K, td, tau):
#Ziegler-Nichols Method
#K   =  steady steady gain
#td  =  dead time
#tau =  time constant

    logger.info("ZN Method : Control Type = {}".format(PID_TYPES[control]))

    tdT = td / tau

    if (control == P_CONTROL):
        Kc = 1.0 /(K * tdT)
        return Kc, 0.0, 0.0
    elif (control == PI_CONTROL):
        Kc = 0.9 / (K * tdT)
        taui = 3.3 * td
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        Kc = 1.2 / (K * tdT)
        taui = 2.0 * td
        taud = 0.5 * td
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def cohen_coon(control, K, td, tau):
#Cohen-Coon Method
#K   =  steady steady gain
#td  =  dead time
#tau =  time constant

    logger.info("Cohen-Coon Method : Control Type = {}".format(PID_TYPES[control]))

    tdT = td / tau

    if (control == P_CONTROL):
        Kc = tau * (1.0 + tdT / 3.0) / (K * td)
        return Kc, 0.0, 0.0
    elif (control == PI_CONTROL):
        Kc = tau * (0.9 + tdT / 12.0) / (K * td)
        taui = td * (30.0 + 3.0 * tdT) / (9.0 + 20.0 * tdT)
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        Kc = tau * (4.0 / 3.0 + tdT / 4.0) / (K * td);
        taui = td * (32.0 + 6.0 * tdT) / (13.0 + 8.0 * tdT);
        taud = td * 4.0 / (11.0 + 2.0 * tdT);
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def ITAE_load(control, K, td, tau):
#ITAE load change Method
#K   =  steady steady gain
#td  =  dead time
#tau =  time constant

    logger.info("ITAE load change Method : Control Type = {}".format(PID_TYPES[control]))

    tdT = td / tau

    if (control == P_CONTROL):
        print("P Control is not supported")
    elif (control == PI_CONTROL):
        a1 = 0.859
        b1 = -0.977
        a2 = 0.674
        b2 = 0.68
        Kc = a1 * (tdT ** b1) / K
        taui = tau * (tdT ** b2) / a2
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        a1 = 1.357
        b1 = -0.947
        a2 = 0.842
        b2 = 0.738
        a3 = 0.381
        b3 = 0.995
        Kc = a1 * (tdT ** b1) / K
        taui = tau * (tdT ** b2) / a2
        taud = a3 * tau * (tdT ** b3)
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def ITAE_set_point(control, K, td, tau):
#ITAE set point change Method
#K   =  steady steady gain
#td  =  dead time
#tau =  time constant

    logger.info("ITAE set point change Method : Control Type = {}".format(PID_TYPES[control]))

    tdT = td / tau

    if (control == P_CONTROL):
        print("P Control is not supported")
    elif (control == PI_CONTROL):
        a1 = 0.586
        b1 = -0.916
        a2 = 1.03
        b2 = -0.165
        Kc = a1 * (tdT ** b1) / K
        taui = tau / (a2 + b2 * tdT)
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        a1 = 0.965
        b1 = -0.855
        a2 = 0.796
        b2 = -0.147
        a3 = 0.308
        b3 = 0.9292
        Kc = a1 * (tdT ** b1) / K
        taui = tau / (a2 + b2 * tdT)
        taud = a3 * tau * (tdT ** b3)
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def direct_synthesis(K, td, tau, tauc = 0):
#Direct synthesis PI Method
#K   =  steady steady gain
#td  =  dead time
#tau =  time constant
#tauc=  system time constant

    logger.info("Direct synthesis PI Method")

    if (tauc == 0):
        tauc = td * 2.0
    Kc = 1.0 * tau / K / (td + tauc)
    taui = tau
    return Kc, taui, 0.0
#-------------------------------------------------------------------------------
def IMC(K, td, tau, tauc = 0):
#IMC PID Method
#K   =  steady steady gain
#td  =  dead time
#tau =  time constant
#tauc=  system time constant

    logger.info("IMC PID Method")

    if (tauc == 0):
        tauc = td * 2.0 / 3.0
    Kc = (1.0 + 2.0 * tau / td) / (1.0 + 2.0 * tauc / td) / K
    taui = tau + td / 2.0
    taud = tau / (1.0 + 2.0 * tau / td)
    return Kc, taui, taud
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
PID_RECIPIES = [ZN, cohen_coon, ITAE_load, ITAE_set_point, direct_synthesis, IMC]
#-------------------------------------------------------------------------------
