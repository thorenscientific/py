'''
Welcome to the LTPyLab simulation of some cool LTC2500 applications.
We'll derive some of the filters used in the LTC2500 family of ADCs,
Then demonstrate that averaging is just the same thing as bin 0 of an FFT.
This is a useful mental tool for relating the AC spec of SNR to the DC spec
of RMS noise.

Next we'll model the input noise of the LTC2500 in the time domain and look at
it in the frequency domain, then vice versa for a resistive sensor (model noise
in frequency, then translate to time.)

Then we'll get a bit more creative and import the noie shape of an LTC2057 from
LTSpice and apply some of the LTC2500 filters to see what total noise we can
expect!


Mark Thoren
Linear Technology Corporation
June, 2015
'''

# First, import goodies from standard libraries
import numpy as np
from scipy import signal
from scipy.misc import imread
from matplotlib import pyplot as plt

# Import Linear Tech functions
from LTPyLab_functions import *




# Select downsample factor. This can be any power of 2 from 4 to 16384
downsample = 64
# Select variable decimation filter decimation factor. This can be any number
# between 1 and 16384. Note that
var_decimation = 1234

# Generate SINC filters. SINC filter coefficients are very easy to generate, so
# we'll just derive them directly.
sinc1 = np.ones(downsample)
sinc2 = np.convolve(sinc1, sinc1)
sinc3 = np.convolve(sinc2, sinc1)
sinc4 = np.convolve(sinc3, sinc1)
varsinc = np.ones(var_decimation)

# Mark's wild stab at a spread-sinc filter
ssinc = np.convolve(sinc1, np.ones(downsample * .625))
ssinc = np.convolve(ssinc, np.ones(downsample * .75))
#ssinc = np.convolve(ssinc, np.ones(downsample * .875))
ssinc = np.convolve(ssinc, np.ones(downsample * .9375))

# We'll normalize the filters here, since this is what the LTC2500 will send
# out
sinc1 = sinc1 / sum(sinc1)
sinc2 = sinc2 / sum(sinc2)
sinc3 = sinc3 / sum(sinc3)
sinc4 = sinc4 / sum(sinc4)
ssinc = ssinc / sum(ssinc)
varsinc = varsinc / sum(varsinc)

# Import SSINC and SSINC + flattening filters here...
# <<TO DO>>


plt.figure(1)
plt.subplot(3, 1, 1)
plt.plot(sinc1)
plt.ylabel('Amplitude')
plt.title('sinc filter time domain responses')
plt.subplot(3, 1, 2)
plt.plot(sinc4)
plt.ylabel('Amplitude')
plt.subplot(3, 1, 3)
plt.plot(ssinc)
plt.ylabel('Amplitude')
#plt.plot(reverser * amax(sinc4))
plt.xlabel('tap number')

#plt.hlines(1, min(sinc4), max(sinc4), colors='r')
#plt.hlines(0, min(sinc4), max(sinc4))
#plt.xlim(xmin=-100, xmax=2*downsample)
#plt.legend(('Unit-Step Response',), loc=0)
plt.grid()
plt.show()

w1, h1 = signal.freqz(sinc1, 1, 16385)
w2, h2 = signal.freqz(sinc2, 1, 16385)
w3, h3 = signal.freqz(sinc3, 1, 16385)
w4, h4 = signal.freqz(sinc4, 1, 16385)
ws, hs = signal.freqz(ssinc, 1, 16385)

fresp1 = 20*np.log10(abs(h1))
fresp2 = 20*np.log10(abs(h2))
fresp3 = 20*np.log10(abs(h3))
fresp4 = 20*np.log10(abs(h4))
fresps = 20*np.log10(abs(hs))


plt.figure(2)
plt.plot(fresp1, zorder=1)
#plt.plot(fresp2, zorder=1)
#plt.plot(fresp3, zorder=1)
plt.plot(fresp4, zorder=1)
plt.plot(fresps, zorder=1)


plt.title('sinc4 frequency domain response')
plt.xlabel('freq.')
plt.ylabel('log Amplitude')
plt.axis([0, 16400, -150, 0])
plt.show()



#Okay, now let's play around with some filtering, and try to show the
#equivalence of averaging (A SINC1 filter) to bin 1 of an FFT!

num_points = 1024
value = 100
rms_noise = 25

data = np.ndarray(shape=num_points, dtype=float)
avg = 0.0
for i in range(num_points):
    data[i] = np.random.normal(value, rms_noise)
    avg += data[i]    
    
avg = avg / num_points
print "Average, calculated using standard method: " + str(avg)
fftdata = np.fft.fft(data)
print "Average, taken as bin 1 of FFT: " + str(fftdata[0] / num_points)


# Now on to modeling the noise of the LTC2500 itself, the noise of a
# resistive sensor, and the noise of an LTC2057

print("Now let's model the noise of the LTC2500 and a resistive source")
resistance = 350
temperature = 300
resistor_noise = np.sqrt(4*1.3806488e-23*temperature*resistance)
fftlength = 8192
samplerate = 1024000
bin_width = samplerate / (2*fftlength)
# Add these calculations (copied from another script...):
#adc_snr = -90.2 # Enter datasheet SNR
#adc_range = 10.0 # Enter peak-to-peak range
# Calculate total ADC noise (volts RMS)
#adc_noise = (10 ** (adc_snr / 20)) * adc_range / (2*2**0.5)

#ADR RMS noise formula: 10^(SNR / 20) * peak-to-peak input range /(2*SQRT2) = RMS Noise


#From the datasheet: 10^(-104dB SNR / 20) * 10V/(2*SQRT2) = 22.3uVRMS
adc_noise = 22.3e-6 
print("ADC total noise: " + str(adc_noise))
print("bin Width: " + str(bin_width))
theo_noise = (adc_noise / np.sqrt(samplerate/2))
print("Theoretical ADC noise density: " + str(theo_noise))


smoothed_adc_psd = np.zeros(fftlength)
averages = 128
for i in range(0, averages):
    # Generate some ADC samples with Gaussian noise. Average a bunch of runs to
    # see where the real noise floor is.
    adc_samples = np.random.normal(loc=0, scale=adc_noise, size=fftlength)
    adc_samples_fft = abs(np.fft.fft(adc_samples))/fftlength
    # Calculate the psd and scale properly - divide FFT by FFT length,
    # Then divied by the bin width to get density directly.
    #### DOUBLE CHECK THIS - the double-sided spectrum amplitude looks a bit low...
#    adc_psd = np.sqrt(adc_samples_fft*adc_samples_fft/bin_width)
    adc_psd = adc_samples_fft/np.sqrt(bin_width)
    
    smoothed_adc_psd += (adc_psd / averages)

#smoothed_adc_psd = np.convolve(np.ones(64), adc_psd)/64

measured_adc_psd = np.average(smoothed_adc_psd)
print("Measured ADC PSD: " + str(measured_adc_psd))
print ("error %" + str(measured_adc_psd/theo_noise))

# Here we're going to do the opposite of what we did with the ADC, that is,
# We're going to model a resistor's noise in the frequency domain and see what it
# looks like in the time domain. There's a couple of subtleties, so
# pay attention!
resistor_psd = np.ones(fftlength)*resistor_noise # Vector representing noise density
resistor_complex_psd = np.ndarray(fftlength, dtype=complex) # Initialize an array to fill up
for i in range(fftlength/2): #Setting two bins for each iteration, working inward from DC, FS
    phase = np.random.uniform(0, 2*np.pi) # Generate a random number from 0 to 2*pi
    real = np.cos(phase) # Find real component of noise vector
    imag = np.sin(phase) # Find imaginary component of noise vector
    resistor_complex_psd[i+1] = ((real) + 1j*imag )*resistor_psd[i+1] # Note that we start at bin 1, not zero!
    resistor_complex_psd[(fftlength-1) - i] = ((real) - 1j*imag)*resistor_psd[(fftlength-1) - i] # Conjugate!
resistor_complex_psd[0] = 0.0 #Take care of DC
resistor_complex_psd[fftlength/2] = resistor_noise #Take care of one bin past Nyquist

# Now find time domain voltage. Check for yourself - is there any imaginary component?
resistor_time_noise = np.fft.ifft(resistor_complex_psd)*fftlength


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
plt.plot(np.abs(resistor_complex_psd))
plt.plot(np.concatenate((ltc2057_psd, ltc2057_psd[::-1])))
plt.show()

t = np.arange(fftlength) # Vector for the X axis

plt.figure(4)
plt.title("350 ohm resistor time noise calculated from\n frequency domain density")
plt.xlabel('time (samples)')
plt.ylabel('Voltage (V)')
#plt.plot(t, resistor_complex_psd.real, 'b-', t, resistor_complex_psd.imag, 'r--')
plt.plot(t, resistor_time_noise.real, 'b-', t, resistor_time_noise.imag, 'r--')
plt.show()

# Above, we found the filter response using the freqz function. You can achieve
# the same thing by taking an fft of the filter taps, padded out to the length
# of the fft that you will be multiplying the response by.
sinc4resp = abs(np.fft.fft(np.concatenate((sinc4,np.zeros(fftlength-int(sinc4.size))))))
sinc4resp_dB = 20*np.log10(sinc4resp)
# now plot...
plt.figure(5)
plt.title("SINC4 filter response from zero-padded coefficients")
plt.plot(sinc4resp_dB)
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

zones_ltc2057_psd, ltc2057_folded = fold_spectrum(wide_ltc2057_psd, points_per_zone, num_zones )


plt.figure(6)
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
plt.setp(lines, color='#00FF00', ls='-') #Green
lines = plt.plot(ltc2057_folded)
plt.setp(lines, color='k', ls='-') #Black
plt.show()

ltc1563_response = np.zeros(16384)
print('reading LTC1563 frequency response to 2M')
infile = open('1563-3_aa_filter_sim.txt', 'r')
print("First line (header): " + infile.readline())
for i in range(1, 16384):
    instring = infile.readline()
    indata = instring.split()         # Each line has two entries separated by a space
    magphase = indata[1]            #EXTREME KLUGE until we use regex properly
    field1 = magphase.split("(")
    field2 = field1[1].split("dB")
    magnitude = field2[0]
    #print magnitude
    ltc1563_response[i] = 10.0 ** (float(magnitude)/20) # Convert from dB to fraction
infile.close()
print('done reading!')


    
# Fold up LTC1563 response
zones_ltc1563_resp, ltc1563_folded = fold_spectrum(ltc1563_response, 4096, 4)
# Now multiply zones by filter response!!
total_resp0 = list(zones_ltc1563_resp[0])
total_resp1 = list(zones_ltc1563_resp[1])
total_resp2 = list(zones_ltc1563_resp[2])
total_resp3 = list(zones_ltc1563_resp[3])

# Multipy analog filter response with the digital filter response, zone by zone
for i in range(0, (fftlength/2)-1):
    total_resp0[i] = total_resp0[i] * sinc4resp[i]
    total_resp1[i] = total_resp1[i] * sinc4resp[i]
    total_resp2[i] = total_resp2[i] * sinc4resp[i]
    total_resp3[i] = total_resp3[i] * sinc4resp[i]

# Plot LTC1563 folded response
plt.figure(7)
plt.title("LTC1563 response to 2.048MHz, folded \nand multiplied by SINC4")
ax = plt.gca()
ax.set_axis_bgcolor('#C0C0C0')
lines = plt.plot(20*np.log10(zones_ltc1563_resp[0]))
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(20*np.log10(zones_ltc1563_resp[1]))
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(20*np.log10(zones_ltc1563_resp[2]))
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(20*np.log10(zones_ltc1563_resp[3]))
plt.setp(lines, color='#00FF00', ls='-') #Green
lines = plt.plot(20*np.log10(ltc1563_folded))
plt.setp(lines, color='k', ls='-') #Black
 # Plot total response of LTC1563 and digital filter on the same graph.
lines = plt.plot(20*np.log10(total_resp0))
plt.setp(lines, color='#FF0000', ls='-') #Red
lines = plt.plot(20*np.log10(total_resp1))
plt.setp(lines, color='#FF7F00', ls='--') #Orange
lines = plt.plot(20*np.log10(total_resp2))
plt.setp(lines, color='#FFFF00', ls='-') #Yellow
lines = plt.plot(20*np.log10(total_resp3))
plt.setp(lines, color='#00FF00', ls='-') #Green
plt.show()

#

ltc2057_total_noise = np.zeros(fftlength*2)
for i in range(1, fftlength*2):
    ltc2057_total_noise[i] = ltc2057_total_noise[i-1] + wide_ltc2057_psd[i]
ltc2057_total_noise = ltc2057_total_noise / ((bin_width / 2) ** 0.5)

plt.figure(8)
plt.title("Integrated LTC2057 noise")
plt.plot(ltc2057_total_noise)
plt.show()
    
    