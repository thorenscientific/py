#-------------------------------------------------------------------------------
# Name:        PIDTuneMainWindow
# Purpose:
#
# Author:      elbar
#
# Created:     11/10/2012
# Copyright:   (c) elbar 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import sys
import logging

from PyQt4 import QtGui,QtCore


from Ui_mainwindow import Ui_MainWindow

import ControlSys  as ctrl 
import Utils
import PlotWidget as plt_
from PIDTuneAbout import PIDTuneAboutWindow
from PIDProccessModel import PIDProccessModelWindow
from PIDCtrlModel import PIDCtrlModelWindow

#create logger
logger = Utils.create_logger(file_name = 'pyPIDTune.log', level = logging.DEBUG)

#-------------------------------------------------------------------------------
class PIDTuneMainWindow(QtGui.QMainWindow):
    """ Class wrapper for main window ui """

    def __init__(self):
        super(PIDTuneMainWindow,self).__init__()
        # Init vars
        self.closed_loop = None # Closed Loop tf
        self.open_loop = None # Open Loop tf        
        # init
        self.setupUI()
        #init plot widgets
        self._proccess_plot = plt_.PlotWidget('Time Domain Proccess Graphs', x_label='t', y_label='mag')
        self._proccess_bode_plot = plt_.PlotWidget('Freq Domain Proccess Graphs', 'log', x_label='w', y_label='mag')        
        self._cl_plot = plt_.PlotWidget('Closed Loop Time Domain Graphs', x_label='t', y_label='mag')
        self._cl_bode_plot = plt_.PlotWidget('Closed Loop Freq Domain Graphs', 'log', x_label='w', y_label='mag')        
        self._cl_nyquist_plot = plt_.PlotWidget('Closed Loop Nyquist Graph', x_label='real', y_label='imag')        
        
    def setupUI(self):
        # create window from ui
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.lblProccess.setStyleSheet('QLabel {background-color : white; color : black;}')
        self.ui.lblPID.setStyleSheet('QLabel {background-color : white; color : black;}')
        # setup toolbar
        # Proccess
        self.ui.mainToolBar.addAction(self.ui.actionProccessTF)
        self.ui.mainToolBar.addAction(self.ui.actionTime_Domain_Graph)
        self.ui.mainToolBar.addAction(self.ui.actionFreq_Domain_Graph)
        self.ui.mainToolBar.addSeparator()
        # PID
        self.ui.mainToolBar.addAction(self.ui.actionPID_Controller)
        self.ui.mainToolBar.addSeparator()
        # Closed Loop
        self.ui.mainToolBar.addAction(self.ui.actionCLTime_Domain_Graph)
        self.ui.mainToolBar.addAction(self.ui.actionCLFreq_Domain_Graph)
        self.ui.mainToolBar.addAction(self.ui.actionCLNyquist_Graph)
        self.ui.mainToolBar.addSeparator()
        # Var
        self.ui.mainToolBar.addAction(self.ui.actionReset_Models)
        self.ui.mainToolBar.addAction(self.ui.actionAbout)
        self.ui.mainToolBar.addAction(self.ui.actionExit)
        # setup dialogs
        self._about_dlg = PIDTuneAboutWindow()
        self._proccess_model_dlg = PIDProccessModelWindow()
        self._pid_ctrl_model_dlg = PIDCtrlModelWindow()
        # signals-slots
        self.ui.actionAbout.triggered.connect(self._about_dlg.show)
        self.ui.actionProccessTF.triggered.connect(self._proccess_model_dlg.open)
        self.connect(self._proccess_model_dlg, QtCore.SIGNAL("proccess_tf_changed"), self._proccess_model_changed)
        self.ui.actionPID_Controller.triggered.connect(self._pid_ctrl_model_dlg.open)
        self.connect(self._pid_ctrl_model_dlg, QtCore.SIGNAL("pid_tf_changed"), self._pid_model_changed)
        self.ui.actionReset_Models.triggered.connect(self._reset_models)
        self.ui.actionTime_Domain_Graph.triggered.connect(self._proccess_time_graphs)
        self.ui.actionFreq_Domain_Graph.triggered.connect(self._proccess_freq_graphs)
        self.ui.actionCLTime_Domain_Graph.triggered.connect(self._cl_time_graphs)
        self.ui.actionCLFreq_Domain_Graph.triggered.connect(self._cl_freq_graphs)
        self.ui.actionCLNyquist_Graph.triggered.connect(self._cl_nyquist_graph)
        # show window
        self.show()
        logger.info("Main Window SetUp finished.")

    def _reset_models(self):
        ''' reset models '''
        # reset proccess model
        self._proccess_model_dlg.k = 0.0
        self._proccess_model_dlg.v1 = []
        self._proccess_model_dlg.v2 = []
        self._proccess_model_dlg.delay = 0.0
        self._proccess_model_dlg.pade = 1
        self._proccess_model_dlg.pade_tf = None
        self._proccess_model_dlg.tf = None
        self._proccess_model_changed()
        # reset pid
        self._pid_ctrl_model_dlg.kc = 0.0
        self._pid_ctrl_model_dlg.ti = 0.0
        self._pid_ctrl_model_dlg.td = 0.0
        self._pid_ctrl_model_dlg.tf = None
        self._pid_model_changed()

    def _proccess_model_changed(self):
        ''' proccess model changed '''
        self.ui.lblProccess.setText(str(self._proccess_model_dlg.tf) +
                            '\nDelay : {0} s'.format(self._proccess_model_dlg.delay) +
                            ', Pade : {0}'.format(self._proccess_model_dlg.pade_order))
        self._pid_ctrl_model_dlg.tf_proccess = self._proccess_model_dlg.tf
        self._cl_model_changed()
        if (self._proccess_plot.plot_dlg.isVisible()):
            self._proccess_time_graphs()
        if (self._proccess_bode_plot.plot_dlg.isVisible()):
            self._proccess_freq_graphs()
        logger.info("Proccess model changed.")

    def _pid_model_changed(self):
        ''' pid model changed '''
        self.ui.lblPID.setText(str(self._pid_ctrl_model_dlg.tf))
        self._cl_model_changed()
        logger.info("PID model changed.")

    def _cl_model_changed(self):
        ''' closed loop model changed
        FB(s) = Proccess * PID / (1 + Proccess * PID)
        open loop model changed
        FB(s) = Proccess * PID
        '''
        if (self._proccess_model_dlg.tf and self._pid_ctrl_model_dlg.tf):
            self.closed_loop = ctrl.TransferFunction()
            self.closed_loop.set_lti(ctrl.closed_loop_lti(self._proccess_model_dlg.tf.lti, self._pid_ctrl_model_dlg.tf.lti))
            self.open_loop = ctrl.TransferFunction()
            self.open_loop.set_lti(ctrl.mul_lti(self._proccess_model_dlg.tf.lti, self._pid_ctrl_model_dlg.tf.lti))
        else:
            self.closed_loop = None
            self.open_loop = None            
        if (self._cl_plot.plot_dlg.isVisible()):
            self._cl_time_graphs()
        if (self._cl_bode_plot.plot_dlg.isVisible()):
            self._cl_freq_graphs()
        if (self._cl_nyquist_plot.plot_dlg.isVisible()):
            self._cl_nyquist_graph()
        if (self.closed_loop):
            logger.info("Closed loop model changed.")
            logger.info("Closed loop Transfer Function = {0}".format(str(self.closed_loop)))
            logger.info("Open loop Transfer Function = {0}".format(str(self.open_loop)))            

    def _proccess_time_graphs(self):
        ''' proccess model time domain graphs '''
        if (self._proccess_model_dlg.tf):
            self._proccess_plot.del_curves()
            t, y = self._proccess_model_dlg.tf.step()            
            self._proccess_plot.add_curve(t, y, 'Step', 'b')
            t, y = self._proccess_model_dlg.tf.impulse()
            self._proccess_plot.add_curve(t, y, 'Impulse', 'r')
            self._proccess_plot.show()
            logger.info("Proccess Time Graphs opened.")
        else:
            logger.warning("Proccess Time Graphs failed > Invalid Proccess Model.")
            Utils.errorMessageBox("Invalid Proccess Model")

    def _proccess_freq_graphs(self):
        ''' proccess model freq domain graphs '''
        if (self._proccess_model_dlg.tf):
            self._proccess_bode_plot.del_curves()
            w, mag, phase = self._proccess_model_dlg.tf.bode()
            self._proccess_bode_plot.add_curve(w, mag, 'Mag', 'b')
            self._proccess_bode_plot.add_curve(w, phase, 'Phase', 'r')
            self._proccess_bode_plot.show()
            logger.info("Proccess Freq Graphs opened.")
        else:
            logger.warning("Proccess Freq Graphs failed > Invalid Proccess Model.")
            Utils.errorMessageBox("Invalid Proccess Model")

    def _cl_time_graphs(self):
        ''' closed loop model time domain graphs '''
        if (self.closed_loop):
            self._cl_plot.del_curves()
            t, y = self.closed_loop.step()
            self._cl_plot.add_curve(t, y, 'Step', 'b')
            t, y = self.closed_loop.impulse()
            self._cl_plot.add_curve(t, y, 'Impulse', 'r')
            self._cl_plot.show()
            logger.info("Closed loop Time Graphs opened.")
        else:
            logger.warning("Closed loop Time Graphs failed > Invalid Proccess Model.")
            Utils.errorMessageBox("Invalid Closed Loop Model")

    def _cl_freq_graphs(self):
        ''' closed loop model freq domain graphs '''
        if (self.open_loop):
            self._cl_bode_plot.del_curves()
            w, mag, phase = self.open_loop.bode()
            self._cl_bode_plot.add_curve(w, mag, 'Mag', 'b')
            self._cl_bode_plot.add_curve(w, phase, 'Phase', 'r')
            self._cl_bode_plot.show()
            logger.info("Closed loop Freq Graphs opened.")
        else:
            logger.warning("Closed loop Freq Graphs failed > Invalid Proccess Model.")
            Utils.errorMessageBox("Invalid Closed Loop Model")

    def _cl_nyquist_graph(self):
        ''' closed loop model nyquist graph '''
        if (self.open_loop):
            self._cl_nyquist_plot.del_curves()
            w, H = self.open_loop.nyquist()
            self._cl_nyquist_plot.add_curve(H.real, H.imag, 'Nyquist', 'b')
            self._cl_nyquist_plot.show()
            logger.info("Closed loop nyquist Graph opened.")
        else:
            logger.warning("Closed loop nyquist Graph failed > Invalid Proccess Model.")
            Utils.errorMessageBox("Invalid Closed Loop Model")

    def closeEvent(self, event):
        ''' main window is closing '''
        logger.info("Main Window is closing.")

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def main():

    logger.info("Program is starting.")
    #create qt application
    app=QtGui.QApplication(sys.argv)
    #load main window
    w = PIDTuneMainWindow()
    #application loop
    res = sys.exit(app.exec_())
    #application loop quited

if __name__ == '__main__':
    main()
#-------------------------------------------------------------------------------