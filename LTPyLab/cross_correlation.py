# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 13:33:38 2014

@author: mark_t
"""

import numpy as np
from numpy import array, vdot, zeros
from scipy import fft, real
#from numpy.random import normal, uniform

def dot_product(a,b):
    dp=np.real(a)*np.real(b) + np.imag(a) * np.imag(b)
    return dp

def alt_dot_product(a, b):
    dp = np.abs(a)*np.abs(b)*np.cos(np.angle(a) - np.angle(b))
    return dp


a = array([1+2j,3+4j])
b = array([5+6j,7+8j])

c = 2+2j
d = 2+2j

#print vdot(a, b)
#(70-8j)
#print vdot(b, a)
#(70+8j)
print np.dot(c, d)
print np.vdot(c, d)
print dot_product(c, d)
print alt_dot_product(c, d)


zero_vector = np.ndarray(shape=(1024), dtype=complex) # Make a complex vector
#for i in range(0, 1024):
#    zero_vector[i] = 0 + 0j
    
xcorr = zero_vector

dut_noise_fft_avg = zeros(1024)
path_a_noise_fft_avg = zeros(1024)
path_b_noise_fft_avg = zeros(1024)
xcorr_avg = zeros(1024)

naverages = 10

for j in range(0, naverages):
    random_phase = np.random.uniform(0.0, 2*3.1415926, 1)
    dut_noise = np.random.normal(0.0, .00025, 1024)
    for i in range(0, 1024):
        dut_noise[i] += .000025 * np.sin(random_phase + (2.0*3.1415926 * 100 * i/1024))
    
    path_a_noise = np.random.normal(0.0, .001, 1024)
    path_b_noise = np.random.normal(0.0, .001, 1024)
    
    dut_noise_fft = fft(dut_noise)
    path_a_noise_fft = fft(path_a_noise + dut_noise)
    path_b_noise_fft = fft(path_b_noise + dut_noise)
    
    
    for i in range(0, 1024):
        xcorr[i] = (dot_product(path_a_noise_fft[i], path_b_noise_fft[i]))

    dut_noise_fft_avg = dut_noise_fft_avg + abs(dut_noise_fft)
    path_a_noise_fft_avg = path_a_noise_fft_avg + abs(path_a_noise_fft)
    path_b_noise_fft_avg = path_b_noise_fft_avg + abs(path_b_noise_fft)
    xcorr_avg = xcorr_avg + xcorr


dut_noise_fft_avg = dut_noise_fft_avg / naverages
path_a_noise_fft_avg = path_a_noise_fft_avg / naverages
path_b_noise_fft_avg = path_b_noise_fft_avg / naverages
xcorr_avg = xcorr_avg / naverages
for i in range(0, 1024):
    xcorr_avg[i] = pow(xcorr_avg[i], 0.5)


#print path_a_noise_fft[0]

#xcorr[0] = vdot(path_a_noise_fft[0], path_b_noise_fft[0])

#print real(xcorr)

from matplotlib import pyplot as plt


#plt.plot(t, s, t, i)
plt.figure(1)

plt.subplot(411)
plt.title('Path A noise')
plt.plot(abs(path_a_noise_fft_avg))

plt.subplot(412)
plt.title('Path B noise')
plt.plot(abs(path_b_noise_fft_avg))

plt.subplot(413)
plt.title('DUT noise')
plt.plot(abs(dut_noise_fft_avg))

plt.subplot(414)
plt.title('Cross correlation avg')
plt.plot(abs(xcorr_avg))
plt.show()

#plt.figure(2)
#
#plt.subplot(411)
#plt.plot(abs(path_a_noise_fft))
#plt.title('Last data')
#plt.subplot(412)
#plt.plot(abs(path_b_noise_fft))
#plt.subplot(413)
#plt.plot(abs(dut_noise_fft))
#plt.subplot(414)
#plt.plot(abs(xcorr))
#plt.show()

#print dut_noise
