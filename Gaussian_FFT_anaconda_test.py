# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
C:\Users\admin\.spyder2\.temp.py
"""

print "hello, world!!"
import matplotlib.pyplot as plt
import numpy as np
mu, sigma = 0, 0.1
s = np.random.normal(mu, sigma, 1000)
f = np.abs(np.fft.fft(s))
print f

count, bins, ignored = plt.hist(s, 30, normed=True)
plt.plot(s)
plt.show()
hex()