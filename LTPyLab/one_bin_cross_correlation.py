# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 13:33:38 2014

@author: mark_t
"""
#from numpy import array, vdot, zeros
import numpy as np
#from scipy import fft, real, welch
#from numpy.random import normal, uniform

pi = np.pi

def dot_product(a,b):
    dp=np.real(a)*np.real(b) + np.imag(a) * np.imag(b)
    return dp

def alt_dot_product(a, b):
    dp = abs(a)*abs(b)*np.cos(np.angle(a) - np.angle(b))
    return dp


a = np.array([1+2j,3+4j])
b = np.array([5+6j,7+8j])
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


zero_vector = np.ndarray(shape=(1024), dtype=complex)# Make a complex vector
    

xcorr = zero_vector

dut_noise_fft_avg = np.zeros(1024)
path_a_noise_fft_avg = np.zeros(1024)
path_b_noise_fft_avg = np.zeros(1024)
xcorr_avg = np.zeros(1024)
dut_noise = np.zeros(1024)
path_b_noise = np.zeros(1024)
path_b_noise = np.zeros(1024)

naverages = 1000 #How many timies to average cross-correlation
signal_bin = 10 #Which bin number to put signal in (num cycles over time record)
path_noise_level = 1
dut_noise_level = 0.5


for j in range(0, naverages):
    random_dut_phase = np.random.uniform(0.0, 2*3.1415926, 1)
    random_path_a_phase = np.random.uniform(0.0, 2*3.1415926, 1)
    random_path_b_phase = np.random.uniform(0.0, 2*3.1415926, 1)
    
    for i in range(0, 1024): # Generate one frequency of signal, plus two paths, all with random phases
        # Noise is a misnomer - this is what we're after!
        dut_noise[i] = dut_noise_level * np.sin(random_dut_phase + (2.0* pi * signal_bin * i/1024))
        path_a_noise = path_noise_level * np.sin(random_path_a_phase + (2.0* pi * signal_bin * i/1024))
        path_b_noise = path_noise_level * np.sin(random_path_b_phase + (2.0* pi * signal_bin * i/1024))
    

    
    
    for i in range(0, 1024):
        xcorr[i] = (dot_product(path_a_noise_fft[i], path_b_noise_fft[i]))

    dut_noise_fft_avg = dut_noise_fft_avg + np.abs(dut_noise_fft)
    path_a_noise_fft_avg = path_a_noise_fft_avg + np.abs(path_a_noise_fft)
    path_b_noise_fft_avg = path_b_noise_fft_avg + np.abs(path_b_noise_fft)
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
plt.plot(abs(path_a_noise_fft_avg))
plt.title('Averages')
plt.subplot(412)
plt.plot(abs(path_b_noise_fft_avg))
plt.subplot(413)
plt.plot(abs(dut_noise_fft_avg))
plt.subplot(414)
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
