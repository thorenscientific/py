# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 10:51:37 2013

@author: elbar
"""
from guiqwt.plot import CurveDialog
from guiqwt.builder import make

class PlotWidget():
    '''GuiQwt Plot'''

    def __init__(self, title, x_axis='lin', x_label='x', y_label='y'):
        '''Init plot and curves'''
        self.plot_dlg = CurveDialog(edit=False, toolbar=False, wintitle=title,
                                    options=dict(xlabel=x_label, ylabel=y_label))
        self.curves = []
        self._x_axis = x_axis
        self._init_plot(x_label, y_label)            

    def _init_plot(self, xlabel, ylabel):
        '''Init plot'''
        self.plot_dlg.get_itemlist_panel().show()
        _plot = self.plot_dlg.get_plot()
        #_label = '{0} = %.2f<br>{1} = %.2f'.format(xlabel, ylabel)
        #_xcursor = make.xcursor(0, 0, _label)
        #_plot.add_item(_xcursor)
        _plot.set_antialiasing(True)
                                    
    def add_curve(self, x, y, title, color):
        '''Add curves'''
        self.curves.append(make.curve(x, y, title=title, color=color))

    def update_curve(self, curve_item, x, y): 
        '''Update curve values'''
        curve_item.set_data(x, y)
        curve_item.plot().replot()

    def del_curves(self):
        '''Delete curves'''
        _plot = self.plot_dlg.get_plot()
        for curve_item in self.curves:
            _plot.del_item(curve_item)
        self.curves = []         
        
    def _plot_items(self):
        '''Plot curve items'''
        _plot = self.plot_dlg.get_plot()
        for curve_item in self.curves:
            _plot.add_item(curve_item)
            _plot.set_axis_scale(curve_item.xAxis(), self._x_axis)
        self.refresh()
 
    def refresh(self):
        '''Refersh plots'''
        _plot = self.plot_dlg.get_plot()
        _plot.do_autoscale()
        self.plot_dlg.adjustSize()

    def show(self):
        '''Show Plot'''
        self._plot_items()
        self.plot_dlg.show()
