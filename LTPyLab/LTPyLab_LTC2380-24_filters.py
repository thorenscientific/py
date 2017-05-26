'''
Welcome to the LTPyLab simulation of some cool LTC2380-24 applications.
We'll derive the filters used in the LTC2380-24 family of ADCs,
Then demonstrate that averaging is just the same thing as bin 0 of an FFT.
This is a useful mental tool for relating the AC spec of SNR to the DC spec
of RMS noise.

Next we'll model the input noise of the LTC2380-24 in the time domain and look at
it in the frequency domain, then vice versa for a resistive sensor (model noise
in frequency, then translate to time.)

Then we'll get a bit more creative and import the noie shape of an LTC2057 from
LTSpice and apply the LTC2380-24 filter to see what total noise we can expect!


Mark Thoren
Linear Technology Corporation
September, 2015
'''

# First, import goodies from standard libraries
import numpy as np
from scipy import signal
from scipy.misc import imread
from matplotlib import pyplot as plt
# Import Linear Tech functions
import LTPyLab_functions as lltf

# Set up parameters
samplerate = 1024000 # Samples per second

# Make this a multiple of 2. That is, analyze at
# least out to samplerate, which will alias to DC.
nyquist_zones_to_consider = 4

# Select downsample factor. This can be any power of 2 from 4 to 16384
n_factor = 16

# This parameter takes some explanation. When calculating the frequency response of
# the filter, we need more than just n_factor points, because all of the n_factor
# points reside in zeros and you wouldn't have an accurate picture of the response.
freq_response_factor = 512

# Calculate FFT length to use. This is the number of points to analyze for each
# double-nyquist zone.
fftlength = n_factor * freq_response_factor

# Next, we'll Generate SINC1 filter coefficients, wich is just a bunch of ones.
# Note that the LTC2380-24 will scale the output automatically for exact
# power-of-2 n_factors, refer to datasheet for scaling of other factors.
sinc1 = np.ones(n_factor)
# Normalize the filter coefficients to unity.
sinc1 = sinc1 / sum(sinc1)

# Compute the frequency response using freqz (traditional method) We're computing
# half the fftlength because freqz gives results halfway around the unit circle,
# while the FFT method below goes all the way around.
w1, sinc1resp_freqz = signal.freqz(sinc1, 1, fftlength/2)
sinc1resp_freqz_dB = 20*np.log10(abs(sinc1resp_freqz))

# You can achieve the same result as the freqz function in a more intuitive way
# by taking an fft of the filter taps, padded out to the length
# of the fft that you will be multiplying the response by.
sinc1resp = abs(np.fft.fft(np.concatenate((sinc1, np.zeros(fftlength - int(sinc1.size)))))) # filter and a bunch more zeros
sinc1resp_dB = 20*np.log10(sinc1resp)
# now plot...
plt.figure(1)
plt.title('sinc1 frequency response from freqz (blue) and\n zero-padded FFT (red), N=' + str(n_factor))
plt.xlabel('freq.')
plt.ylabel('log Amplitude')
plt.axis([0, fftlength, -50, 0])
lines = plt.plot(sinc1resp_freqz_dB, zorder=1)
plt.setp(lines, color='#0000FF', ls='-') #Blue
lines = plt.plot(sinc1resp_dB)
plt.setp(lines, color='#FF0000', ls='--') #Blue
plt.show()

#Okay, now let's play around with some filtering, and try to show the
#equivalence of averaging (A SINC1 filter) to bin 1 of an FFT!

# Now on to modeling the noise of the LTC2500 itself, the noise of a
# resistive sensor, and the noise of an LTC2057

print("Now let's model the noise of the LTC2500 and a resistive source")
resistance = 350
temperature = 300
resistor_noise = np.sqrt(4*1.3806488e-23*temperature*resistance)

bin_width = samplerate / (2*fftlength)
#From the datasheet: 10^(-104dB SNR / 20) * 10V/(2*SQRT2) = 22.3uVRMS
adc_noise = 22.3e-6 
print("ADC total noise: " + str(adc_noise))
print("bin Width: " + str(bin_width))
print("ADC noise density: " + str(adc_noise / np.sqrt(samplerate/2)))


smoothed_adc_psd = np.zeros(fftlength)
averages = 128
for i in range(0, averages):
    # Generate some ADC samples with Gaussian noise. Average a bunch of runs to
    # see where the real noise floor is.
    adc_samples = np.random.normal(loc=0, scale=adc_noise, size=fftlength)
    # Calculate the psd and scale properly - divide FFT by FFT length,
    # Then divied by the bin width to get density directly.
    #### DOUBLE CHECK THIS - the double-sided spectrum amplitude looks a bit low...
    adc_psd = (abs(np.fft.fft(adc_samples))/fftlength)/np.sqrt(bin_width)
    smoothed_adc_psd += (adc_psd / averages)


# Example SPICE directive: .noise V(Vout2) Vin_source lin 16383 62.5 2048000
# Arguments are output node, input node, linear spacing, # of points, bin 1 frequency, end frequency

ltc2057_psd = np.zeros(fftlength/2) # bin zero(DC) already set to zero ;)
print('reading noise PSD data from file')
infile = open('ltspice_psd.txt', 'r')
print("First line (header): " + infile.readline())
for i in range(1, fftlength/2):
    instring = infile.readline()
    indata = instring.split()         # Each line has two entries separated by a space
    ltc2057_psd[i] = float(indata[1]) # Frequency Density
infile.close()
print('done reading!')


plt.figure(3)
plt.title("ADC, LTC2057, 350 ohm resistor noise")
plt.xlabel('FFT bin number')
plt.ylabel('noise density (V/rootHz)')
plt.plot(smoothed_adc_psd)
plt.plot(np.concatenate((ltc2057_psd, ltc2057_psd[::-1])))
plt.show()





wide_ltc2057_psd = np.zeros(fftlength*2) # bin zero(DC) already set to zero ;)
print('reading wide (2MHz) noise PSD data from file')
infile = open('LTC2057_noisesim_2Meg.txt', 'r')
print("First line (header): " + infile.readline())
for i in range(1, fftlength*2):
    instring = infile.readline()
    indata = instring.split()         # Each line has two entries separated by a space
    wide_ltc2057_psd[i] = float(indata[1]) # Frequency Density
infile.close()
print('done reading!')

#Okay now let's fold zones.
num_zones = 4
points_per_zone = 4096

zones_ltc2057_psd, ltc2057_folded = lltf.fold_spectrum(wide_ltc2057_psd, points_per_zone, num_zones )

print("Size of zones_ltc2057_psd 2d array:")
print len(zones_ltc2057_psd)

plt.figure(4)
plt.title("2.048MHz worth of LTC2057 noise,\nFolded into 4 Nyquist zones")
ax = plt.gca()
ax.set_axis_bgcolor('#C0C0C0')
lines = plt.plot(zones_ltc2057_psd[0])
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(zones_ltc2057_psd[1])
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(zones_ltc2057_psd[2])
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(zones_ltc2057_psd[3])
plt.setp(lines, color='#00FF00', ls='--') #Green
lines = plt.plot(ltc2057_folded)
plt.setp(lines, color='k', ls='-') #Black
plt.show()


# Now multiply zones by filter response!!
total_resp0 = list(zones_ltc2057_psd[0])
total_resp1 = list(zones_ltc2057_psd[1])
total_resp2 = list(zones_ltc2057_psd[2])
total_resp3 = list(zones_ltc2057_psd[3])

# Multipy analog filter response with the digital filter response, zone by zone
for i in range(0, (fftlength/2)-1):
    total_resp0[i] = total_resp0[i] * sinc1resp[i]
    total_resp1[i] = total_resp1[i] * sinc1resp[i]
    total_resp2[i] = total_resp2[i] * sinc1resp[i]
    total_resp3[i] = total_resp3[i] * sinc1resp[i]

# Plot LTC1563 folded response
plt.figure(5)
plt.title("LTC2057 noise to 2.048MHz, folded \nand multiplied by SINC1")
ax = plt.gca()
ax.set_axis_bgcolor('#C0C0C0')
lines = plt.plot(zones_ltc2057_psd[0])
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(zones_ltc2057_psd[1])
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(zones_ltc2057_psd[2])
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(zones_ltc2057_psd[3])
plt.setp(lines, color='#00FF00', ls='--') #Green
lines = plt.plot(ltc2057_folded)
plt.setp(lines, color='k', ls='-') #Black
 # Plot total response of LTC1563 and digital filter on the same graph.
lines = plt.plot(total_resp0)
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(total_resp1)
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(total_resp2)
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(total_resp3)
plt.setp(lines, color='#00FF00', ls='--') #Green
plt.show()

#



ltc2057_total_noise = np.zeros(fftlength*2)
ltc2057_filtered_total_noise = np.zeros(fftlength/2)
for i in range(1, fftlength*2):
    ltc2057_total_noise[i] = ltc2057_total_noise[i-1] + wide_ltc2057_psd[i]
for i in range(1, fftlength/2-1):
    ltc2057_filtered_total_noise[i] = ltc2057_filtered_total_noise[i-1] + total_resp0[i] + total_resp1[i] + total_resp2[i] + total_resp3[i]
    
ltc2057_total_noise = ltc2057_total_noise / ((bin_width / 2) ** 0.5)
ltc2057_filtered_total_noise = ltc2057_filtered_total_noise  / ((bin_width / 2) ** 0.5)

plt.figure(6)
plt.title("Integrated LTC2057 noise and integrated\nnoise after filtering")
plt.plot(ltc2057_total_noise)
plt.plot(ltc2057_filtered_total_noise)
plt.show()




wide_filter = np.concatenate((sinc1resp, sinc1resp))
wide_filtered_psd = wide_filter * wide_ltc2057_psd


integrated_psd = lltf.integrate_psd(wide_filtered_psd, 1.0)


plt.figure(7)
plt.title("Let's do the same thing, but unfolded now")
plt.plot(wide_ltc2057_psd)
plt.plot(wide_filter * np.max(wide_ltc2057_psd))
plt.plot(wide_filtered_psd)
plt.plot(integrated_psd)

if(False):
    # Now for some more fun... Let's see what the total response of the digital filter and analog
    # AAF filter is. For each point on the frequency axis, a first-order analog AAF with a cutoff
    # frequency of f is multiplied by the digital filter response, then integrated across the whole axis.
    n_factor = 64
    points_per_coeff = 128
    filter_coeffs = np.ones(n_factor) / n_factor # Generate the filter
    fresp = lltf.freqz_by_fft(filter_coeffs, points_per_coeff)
    wide_filter = np.concatenate((fresp, fresp))
    
    
    factor = 16
    first_order_response = np.ndarray(len(wide_filter), dtype=float)
    product_integral = np.ndarray(len(wide_filter)/factor, dtype=float)
    downsampled_wide_filter = np.ndarray(len(wide_filter)/factor, dtype=float)
    
    
    for points in range(1, len(wide_filter)/factor):
        for i in range(0, len(wide_filter)): # Generate first order response for each frequency in wide response
            cutoff = float(points*factor)
            first_order_response[i] = 1.0 / (1.0 + (i/cutoff)**2.0)**0.5 # Magnitude = 1/SQRT(1 + (f/fc)^2)
        print ("Haven't crashed, we're on point " + str(points))
    #    plt.figure(8)
    #    plt.plot(first_order_response)
        composite_response = first_order_response * wide_filter
        datapoint = lltf.integrate_psd(composite_response, 1.0 / (n_factor))
        product_integral[points] = datapoint[len(wide_filter)-1]
        downsampled_wide_filter[points] = wide_filter[points * factor]
    
    product_integral_dB = 20*np.log10(product_integral)
    
    plt.figure(9)
    #plt.plot(wide_filter)
    plt.axis([1, 1024, 0.01, 1])
    plt.loglog(product_integral)
    plt.loglog(downsampled_wide_filter)
    plt.show()
