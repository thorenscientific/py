#-------------------------------------------------------------------------------
# Name:        PIDCtrlModelWindow
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
from Ui_pid_ctrl_model import Ui_PIDCtrlModel

import ControlSys  as ctrl 
import Utils
import PIDRecipe

_TF_PID_STD = '''\
          1                 Td * s
Kc * ( 1  + -----  +    ---------------- )
              Ti * s       (Td / N) * s + 1\
'''
_TF_PID_PARALLEL = '''\
       Ki          Kd * s
Kc  +  ---  +   ------------
          s        Tf * s + 1\
'''

#load logger
logger = logging.getLogger("PIDTuneLog")

#-------------------------------------------------------------------------------
class PIDCtrlModelWindow(QtGui.QDialog):
    """ Class wrapper for about window ui """

    def __init__(self):
        super(PIDCtrlModelWindow,self).__init__()
        # Init vars
        self.kc = 0.0
        self.ti = 0.0
        self.td = 0.0
        self.delay = 0.0
        self.tf = None
        self.tf_proccess = None
        # init
        self.setupUI()
        self.ui.lblTF.setText(_TF_PID_STD)
        self.ui.leTi.setEnabled(False)
        self.ui.leTd.setEnabled(False)
        self.ui.leTf.setEnabled(False)

    def setupUI(self):
        # create window from ui
        self.ui=Ui_PIDCtrlModel()
        self.ui.setupUi(self)
        self.ui.lblTF.setStyleSheet('QLabel {background-color : white; color : black;}')
        # signals-slots
        self.ui.buttonBox.clicked.connect(self._button_clicked)
        self.ui.chbTi.clicked.connect(self._update_ui)
        self.ui.chbTd.clicked.connect(self._update_ui)
        self.ui.chbTd.clicked.connect(self._update_ui)
        self.ui.cmbPIDType.currentIndexChanged.connect(self._PID_type_changed)
        self.ui.cmbTuneMethod.currentIndexChanged.connect(self._PID_tune_method_changed)
        self.ui.cmbPIDConfig.currentIndexChanged.connect(self._PID_config_changed)
        # populate PID Methods combo box
        for i in PIDRecipe.PID_METHODS:
            self.ui.cmbTuneMethod.addItem(i)
        logger.info("PID Ctrl Window SetUp finished.")

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
        # Kc input
        _kc = Utils.str_is_num((self.ui.leKc.text()))
        if (not _kc):
            Utils.errorMessageBox("Invalid kc")
            return False
        # Ti input
        if (self.ui.chbTi.isChecked()):
            _ti = Utils.str_is_num(str(self.ui.leTi.text()))
            if (not _ti):
                Utils.errorMessageBox("Invalid Ti")
                return False
        else:
            _ti = 0.0
        # Td input
        if (self.ui.chbTd.isChecked()):
            _td = Utils.str_is_num(str(self.ui.leTd.text()))
            if (not _td):
                Utils.errorMessageBox("Invalid Td")
                return False
        else:
            _td = 0.0
        # Tf input
        if (self.ui.chbTd.isChecked()):
            _delay = Utils.str_is_num(str(self.ui.leTf.text()))
            if (not _delay):
                Utils.errorMessageBox("Invalid Tf / N")
                return False
        else:
            _delay = 0.0
        # set values
        self.kc = _kc
        self.ti = _ti
        self.td = _td
        self.delay = _delay
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
        ''' build selected tranfer function '''
        _idx = self.ui.cmbPIDType.currentIndex()
        if (_idx == 0): # PID STANDARD
            self._build_std_tf()
        elif (_idx == 1): # PID PARALLEL
            self._build_parallel_tf()
        elif (_idx == 2): # Predifined STANDARD PIDs
            self._build_std_tf()

    def _build_std_tf(self):
        ''' build STD tranfer function '''
        _num = []
        _den = []
        # PID(s) = Kc * [(Ti * Td * s^2 / N + (Ti + Td / N) * s + 1)] / [(Ti * Td * s^2 / N + Ti * s)]
        if (self.ti and self.td): # PID
            _num = [(self.ti * self.td) / self.delay, (self.ti + self.td) / self.delay, 1]
            _num [:] = [self.kc * x for x in _num]
            _den = [(self.ti * self.td) / self.delay, self.ti, 0]
        # PI(s) = Kc * [(Ti * s + 1)] / [Ti * s]
        elif (self.ti and not self.td): # PI
            _num = [self.ti, 1]
            _num [:] = [self.kc * x for x in _num]
            _den = [self.ti, 0]
        # PD(s) = Kc * [(Td / N + Td ) * s + 1)] / [(Td * s / N + 1)]
        elif (not self.ti and self.td): # PD
            _num = [self.td / self.delay + self.delay, 1]
            _num [:] = [self.kc * x for x in _num]
            _den = [ self.td / self.delay, 1]
        # P(s) = [ Kc ]
        else : # P
            _num = [self.kc]
            _den = [1]
        self.tf = ctrl.TransferFunction(_num, _den)
        # emit SIGNAL for updating UI
        self.emit(QtCore.SIGNAL("pid_tf_changed"))
        logger.info("Controller Standard Transfer Function = {0}".format(self.tf))

    def _build_parallel_tf(self):
        ''' build PARALLEL tranfer function '''
        _num = []
        _den = []
        # PID(s) = [(Kc * Tf + Kd) * s^2 + (Kc + Ki * Tf) * s + 1)] / [Tf * s^2  + s]
        if (self.ti and self.td): # PID
            _num = [self.kc * self.delay + self.td, self.kc + self.ti * self.delay, self.ti]
            _den = [self.delay, 1, 0]
        # PI(s) = [(Kc * s + Ki)] / [s]
        elif (self.ti and not self.td): # PI
            _num = [self.kc, self.ti]
            _den = [1, 0]
        # PD(s) = [(Kc * Tf + Kd) * s + Kc)] / [Tf * s + 1]
        elif (not self.ti and self.td): # PD
            _num = [self.kc * self.delay + self.td, self.kc]
            _den = [ self.delay, 1]
        # P(s) = [ Kc ]
        else : # P
            _num = [self.kc]
            _den = [1]
        self.tf = ctrl.TransferFunction(_num, _den)
        # emit SIGNAL for updating UI
        self.emit(QtCore.SIGNAL("pid_tf_changed"))
        logger.info("Controller Standard Transfer Function = {0}".format(self.tf))

    def showEvent(self,QShowEvent):
        ''' set values for controls '''
        self.ui.leKc.setText(str(self.kc))
        self.ui.leTi.setText(str(self.ti))
        self.ui.leTd.setText(str(self.td))
        self.ui.leTf.setText(str(self.delay))
        # init ui
        self._PID_type_changed(self.ui.cmbPIDType.currentIndex())

    def _PID_type_changed(self, idx):
        ''' PID type changed '''
        if (idx == 0): # PID STANDARD
            self.ui.lblTF.setText(_TF_PID_STD)
            self.ui.cmbTuneMethod.setEnabled(False)
            self.ui.cmbPIDConfig.setEnabled(False)
            self.ui.chbTi.setEnabled(True)
            self.ui.chbTd.setEnabled(True)
            self.ui.leKc.setEnabled(True)
            self.ui.chbTi.setText('Ti')
            self.ui.chbTd.setText('Td')
            self.ui.lblTf.setText('N')
            self.ui.leTf.setText('10.0')
            self._update_ui()
        elif (idx == 1): # PID PARALLEL
            self.ui.lblTF.setText(_TF_PID_PARALLEL)
            self.ui.cmbTuneMethod.setEnabled(False)
            self.ui.cmbPIDConfig.setEnabled(False)
            self.ui.chbTi.setEnabled(True)
            self.ui.chbTd.setEnabled(True)
            self.ui.leKc.setEnabled(True)
            self.ui.chbTi.setText('Ki')
            self.ui.chbTd.setText('Kd')
            self.ui.lblTf.setText('Tf')
            self.ui.leTf.setText('0.1')
            self._update_ui()
        else: # Predifined STANDARD PIDs
            if (self.tf_proccess and self.tf_proccess.is_FODT == True): # only for FOTD
                self.ui.lblTF.setText(_TF_PID_STD)
                self.ui.cmbTuneMethod.setEnabled(True)
                self.ui.cmbPIDConfig.setEnabled(True)
                self.ui.chbTi.setEnabled(False)
                self.ui.chbTd.setEnabled(False)
                self.ui.leKc.setEnabled(False)
                self.ui.leTi.setEnabled(False)
                self.ui.leTd.setEnabled(False)
                self.ui.leTf.setEnabled(False)
                self.ui.chbTi.setText('Ti')
                self.ui.chbTd.setText('Td')
                self.ui.lblTf.setText('N')
                self.ui.leTf.setText('10.0')
                self._chk_Ti_Td_update()
                self._set_pred_PID_params()
            else:
                Utils.errorMessageBox("Invalid selection.Selection requires First Order with Delay transfer function.")
                self.ui.cmbPIDType.setCurrentIndex(0)

    def _PID_tune_method_changed(self, idx):
        ''' tune method changed '''
        # populate PID Types combo box
        self.ui.cmbPIDConfig.clear()
        for i in PIDRecipe.PID_METHODS_TYPES[idx]:
            self.ui.cmbPIDConfig.addItem(PIDRecipe.PID_TYPES[i])
        self._chk_Ti_Td_update()

    def _PID_config_changed(self):
        ''' PID config changed '''
        self._chk_Ti_Td_update()
        if (self.tf_proccess and self.tf_proccess.is_FODT == True): # only for FOTD
            self._set_pred_PID_params()

    def _chk_Ti_Td_update(self):
        ''' update check status of Ti, Td '''
        _method = PIDRecipe.PID_METHODS_TYPES[self.ui.cmbTuneMethod.currentIndex()]
        _cfg = _method[self.ui.cmbPIDConfig.currentIndex()]
        if (_cfg == 0): # P
            self.ui.chbTd.setChecked(False)
            self.ui.chbTi.setChecked(False)
        elif (_cfg == 1): # PI
            self.ui.chbTd.setChecked(False)
            self.ui.chbTi.setChecked(True)
        elif (_cfg > 1): # PID
            self.ui.chbTd.setChecked(True)
            self.ui.chbTi.setChecked(True)

    def _set_pred_PID_params(self):
        ''' set PID params for predefined PIDs '''
        _method = PIDRecipe.PID_METHODS_TYPES[self.ui.cmbTuneMethod.currentIndex()]
        _cfg = _method[self.ui.cmbPIDConfig.currentIndex()]
        _k = self.tf_proccess.k_FODT
        _t = self.tf_proccess.t_FODT
        _delay = self.tf_proccess.delay
        _kc, _ti, _td = PIDRecipe.PID_RECIPIES[self.ui.cmbTuneMethod.currentIndex()](_cfg, _k, _t, _delay)
        self.ui.leKc.setText('{:.3}'.format(_kc))
        self.ui.leTi.setText('{:.3}'.format(_ti))
        self.ui.leTd.setText('{:.3}'.format(_td))

    def _update_ui(self):
        ''' update ui '''
        self.ui.leTi.setEnabled(self.ui.chbTi.isChecked())
        self.ui.leTd.setEnabled(self.ui.chbTd.isChecked())
        self.ui.leTf.setEnabled(self.ui.chbTd.isChecked())


#-------------------------------------------------------------------------------