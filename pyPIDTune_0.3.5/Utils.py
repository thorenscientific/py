#-------------------------------------------------------------------------------
# Name:        Utils
# Purpose:
#
# Author:      Elbar
#
# Created:     01/03/2012
# Copyright:   (c) USER 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from PyQt4 import QtGui
import logging

#-------------------------------------------------------------------------------
def errorMessageBox(msg):
    ''' Mesaage Box '''
    QtGui.QMessageBox.critical(None,"Error",msg,QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton)

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def str_extract_num(str_in):
    ''' Extract numbers from a string '''
    res = []
    if (str_in):
        for s in str_in.split():
            f = str_is_num(s)
            if (f != None):
                res.append(f)
            else:
                res = None
                break
    return res

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def str_is_num(str_in):
    ''' Check a string if it is number '''
    res = None
    try:
        res = float(str_in)
    except:
        res = None
    return res

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def is_zero(var):
    ''' Check if a list has all its values set to 0 or
        a number is 0
    '''
    res = False
    if (isinstance(var,list)): # list
        for i in var:
            if (i != None and i != 0):
                res = True
    else: # number
        if (var != None and var != 0):
            res = True
    return res

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def create_logger(file_name=None, level=logging.DEBUG):
    ''' Create a logger '''
    logger = logging.getLogger("PIDTuneLog")
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if (file_name):
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger

#-------------------------------------------------------------------------------
