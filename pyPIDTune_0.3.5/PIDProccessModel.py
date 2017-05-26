#-------------------------------------------------------------------------------
# Name:        PIDProccessModelWindow
# Purpose:
#
# Author:      elbar
#
# Created:     09/11/2012
# Copyright:   (c) elbar 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from PyQt4 import QtGui,QtCore
import logging
from Ui_proccess_model import Ui_ProccessModel

from numpy import polymul
import ControlSys  as ctrl 
import Utils

_TF_NUM_DEN = "<b>K * Num(s)<br>-----------<br>    Den(s)</b>"
_TF_ZERO_POLES = "<b>K * (s - z1) (s - z2) ...<br>-----------------------------<br>     (s - p1) (s - p2) ...</b>"
_TF_TIME_CONST = "<b>    K<br>-------------------<br>(t1s + 1) (t2s + 1)</b>"
_TF_1ORDER_WITH_DELAY = "<b>    K<br>-----<br>ts + 1</b>"

#load logger
logger = logging.getLogger("PIDTuneLog")

#-------------------------------------------------------------------------------
class PIDProccessModelWindow(QtGui.QDialog):
    """ Class wrapper for about window ui """

    def __init__(self):
        super(PIDProccessModelWindow,self).__init__()
        # Init vars
        self.k = 0.0
        self.v1 = []
        self.v2 = []
        self.delay = 0.0
        self.pade_order = 1
        self.tf = None
        # init
        self.setupUI()

    def setupUI(self):
        # create window from ui
        self.ui=Ui_ProccessModel()
        self.ui.setupUi(self)
        self.ui.lblVar1.setText("Numerator")
        self.ui.lblVar2.setText("Denominator")
        self.ui.lblTF.setStyleSheet('QLabel {background-color : white; color : black;}')
        self.ui.lblTF.setText(_TF_NUM_DEN)
        # signals-slots
        self.ui.cmbTFForm.currentIndexChanged.connect(self._TFTorm_changed)
        self.ui.buttonBox.clicked.connect(self._button_clicked)
        logger.info("PID Proccess Window SetUp finished.")

    def _TFTorm_changed(self, idx):
        '''change labels'''
        self.ui.leGain.setText('0.0')
        self.ui.leVar1.setText('')
        self.ui.leVar2.setText('')
        self.ui.leDelay.setText('0.0')
        self.ui.sbPadeOrder.setValue(1)
        if (idx == 0): # F(s) = K * Num(s) / Den(s)
            self.ui.lblVar1.setVisible(True)
            self.ui.leVar1.setVisible(True)
            self.ui.lblVar1.setText("Numerator")
            self.ui.lblVar2.setText("Denominator")
            self.ui.lblTF.setText(_TF_NUM_DEN)
        elif (idx == 1): # F(s) = K * (s - z1) (s - z2) ... / (s - p1) (s - p2) ...
            self.ui.lblVar1.setVisible(True)
            self.ui.leVar1.setVisible(True)
            self.ui.lblVar1.setText("Zero")
            self.ui.lblVar2.setText("Poles")
            self.ui.lblTF.setText(_TF_ZERO_POLES)
        elif (idx == 2): # F(s) = K * 1 / (t1s + 1) (t2s + 1)
            self.ui.lblVar1.setVisible(True)
            self.ui.leVar1.setVisible(True)
            self.ui.lblVar1.setText("t1")
            self.ui.lblVar2.setText("t2")
            self.ui.lblTF.setText(_TF_TIME_CONST)
        elif (idx == 3): # F(s) = K * 1 / (ts + 1)
            self.ui.lblVar1.setVisible(False)
            self.ui.leVar1.setVisible(False)
            self.ui.lblVar2.setText("t")
            self.ui.lblTF.setText(_TF_1ORDER_WITH_DELAY)

    def _button_clicked(self, bt):
        ''' check witch button clicked '''
        _br = self.ui.buttonBox.buttonRole(bt)
        if (_br == QtGui.QDialogButtonBox.AcceptRole): # OK
            self._OK_clicked()
        elif (_br == QtGui.QDialogButtonBox.RejectRole): # Cancel
            self._cancel_clicked()
        elif (_br == QtGui.QDialogButtonBox.ApplyRole): # Apply
            self._apply_clicked()
        else:
            self.reject()

    def _cancel_clicked(self):
        ''' cancel changes '''
        logger.info("Cancel changes and exit.")
        self.reject()

    def _check_inputs(self):
        ''' check inputs '''
        idx = self.ui.cmbTFForm.currentIndex()
        # K input
        _k = Utils.str_is_num((self.ui.leGain.text()))
        if (not Utils.is_zero(_k)):
            Utils.errorMessageBox("Invalid k")
            return False
        # Var1 inputs
        _v1 = Utils.str_extract_num(str(self.ui.leVar1.text()))
        if (not Utils.is_zero(_v1) and not idx == 3): # not used in 1st order with delay
            Utils.errorMessageBox("Invalid parameters in {0}".format(self.ui.lblVar1.text()))
            return False
        # Var2 inputs
        _v2 = Utils.str_extract_num(str(self.ui.leVar2.text()))
        if (not Utils.is_zero(_v2) and not idx == 2): # only t2 can be 0
            Utils.errorMessageBox("Invalid parameters in {0}".format(self.ui.lblVar2.text()))
            return False
        # check num/den orders
        if (len(_v1) > len(_v2)):
            Utils.errorMessageBox("Numerator's order is higher than Denominator's")
            return False
        # check delay
        _delay = Utils.str_is_num(self.ui.leDelay.text())
        if (_delay == None or _delay < 0.0 or (_delay == 0.0 and idx == 3)):
            Utils.errorMessageBox("Invalid delay")
            return False
        # set values
        self.k = _k
        self.v1 = _v1
        self.v2 = _v2
        self.delay = _delay
        self.pade_order = self.ui.sbPadeOrder.value()
        return True

    def _OK_clicked(self):
        ''' accept changes '''
        if (self._check_inputs()):
            self._build_tf()
            logger.info("Accept changes and exit.")
            self.accept()

    def _apply_clicked(self):
        ''' apply changes '''
        if (self._check_inputs()):
            logger.info("Apply changes.")
            self._build_tf()

    def _build_tf(self):
        ''' build tranfer function '''
        idx = self.ui.cmbTFForm.currentIndex()
        if (idx == 0): # F(s) = K * Num(s) / Den(s)
            _num = [self.k * x for x in self.v1]
            _den = self.v2
            self.tf = ctrl.TransferFunction(_num, _den, self.delay, self.pade_order)
        elif (idx == 1): # F(s) = K * (s - z1) (s - z2) ... / (s - p1) (s - p2) ...
            _k_num = [self.k]
            _k_den = [1]
            _length = max([len(self.v1), len(self.v2)])
            _zeros = []
            _poles = []
            for i in range(_length):
                if i >= len(self.v1): # num
                    _num = [1]
                else:
                    _num = [1, -self.v1[i]]
                if i >= len(self.v2): # den
                    _den = [1]
                else:
                    _den = [1, -self.v2[i]]
                _zeros.append(_num)
                _poles.append(_den)
            _tf_num = _k_num
            for i in _zeros:
                _tf_num = polymul(_tf_num, i)
            _tf_den = _k_den
            for i in _poles:
                _tf_den = polymul(_tf_den, i)
            self.tf = ctrl.TransferFunction(_tf_num, _tf_den, self.delay, self.pade_order)
        elif (idx == 2): # F(s) = K * 1 / (t1s + 1) (t2s + 1)
            _num = [self.k]
            _den1 = [self.v1[0], 1] # only the first input !
            _den2 = [self.v2[0], 1] # only the first input !
            _tf_num = _num
            _tf_den = polymul(_den1, _den2)
            self.tf = ctrl.TransferFunction(_tf_num, _tf_den, self.delay, self.pade_order)
        elif (idx == 3): # F(s) = K * 1 / (ts + 1)
            _num = [self.k]
            _den = [self.v2[0], 1] # only the first input !
            _tf_num = _num
            _tf_den = polymul(_den1, _den2)
            self.tf = ctrl.TransferFunction(_num, _den, self.delay, self.pade_order)
        # is FODT [First Order with Delay]
        if (self.tf != None and len(self.tf.num) == 1 and len(self.tf.den) == 2 and self.delay > 0.0):
            self.tf.is_FODT = True
            self.tf.k_FODT = self.k
            self.tf.t_FODT = self.v2[0]
            self.tf.delay_FODT = self.delay
        else:
            self.tf.is_FODT = False            
        # emit SIGNAL for updating UI
        self.emit(QtCore.SIGNAL("proccess_tf_changed"))
        logger.info("Transfer Function = {0}".format(self.tf))

    def showEvent(self,QShowEvent):
        ''' set values for controls '''
        self.ui.leGain.setText(str(self.k))
        self.ui.leDelay.setText(str(self.delay))
        self.ui.sbPadeOrder.setValue(self.pade_order)
        _leVal = ''
        for i in self.v1:
            _leVal = _leVal + str(i) + " "
        self.ui.leVar1.setText(_leVal)
        _leVal = ''
        for i in self.v2:
            _leVal = _leVal + str(i) + " "
        self.ui.leVar2.setText(_leVal)

#-------------------------------------------------------------------------------