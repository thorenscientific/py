# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from matplotlib import pyplot as plt
import numpy as np

def parabola(x, a, b, c):
    return a*(x**2) + b*x + c
    
def priyabola(x):
    a = -25.0/108.0
    b = 263.0/54.0
    c = -184/27.0
    return parabola(x, a, b, c)
    
xaxis = np.linspace(-2, 22, num=50, endpoint = True)

birdpath = priyabola(xaxis)

plt.figure(1)
plt.title("Priya's Priyabola!")
plt.plot(xaxis, birdpath)