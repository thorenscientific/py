#from numpy import min, max, convolve, random
import numpy as np
from scipy import linspace, fft
from scipy import signal
from scipy.signal import lti, step
from scipy.misc import imread
from matplotlib import pyplot as plt



#first, let's make a sinewave


#Okay, now on to the illustrated FFT!!!
num_bins = 32 #This is also the number of points in the time record
bin_number = 5.0
data = np.zeros(num_bins)
#Generate some input data
for i in range(num_bins):
    data[i]= np.sin(2*np.pi*bin_number*i/num_bins)
    
plt.figure(1)
plt.subplot(211)
plt.title("Original signal")
plt.plot(data)
plt.show

upsample = 16
upsample_data = np.zeros(upsample*len(data))
for i in range (0, len(data)):
        for j in range (0, upsample):
            upsample_data[i*upsample+j] = data[i]
print "length of upsampled data:" + str(len(upsample_data))
plt.figure(4)
plt.subplot(211)
plt.plot(upsample_data)
plt.show
#upsample_data = convolve(upsample_data, ones(upsample))

dac_spectrum = (abs(fft(upsample_data)))
plt.subplot(212)
plt.plot(dac_spectrum)#, '-o')
plt.show

#Okay, now on to quantization noise. Why is this not talked about very often?
# We're thinking because most of the time the quantization noise is quite
# a bit lower than noise from other sources. So let's start with an ideal
# DAC output, and put some noise into the steps. Reminder: We're trying
# to see stuff in the frequency domain that is between the clock products
# that we just simulated, so we need several cycles to work with.
# More cycles = a closer look at the shape of the quantization noise floor.
num_cycles = 16
upsample_data_w_qnoise = np.zeros(upsample*len(data)*num_cycles)
for h in range (0, num_cycles):
    for i in range (0, len(data)):
        qnoise = np.random.uniform(0, 0.1, 1)
        for j in range (0, upsample):
            upsample_data_w_qnoise[h*upsample*len(data) + i*upsample + j] = data[i] + qnoise
dac_spectrum_w_qnoise = (abs(fft(upsample_data_w_qnoise)))
plt.figure(5)
plt.plot(dac_spectrum_w_qnoise)
plt.show

plt.figure(6)
plt.plot(upsample_data_w_qnoise)
plt.show


