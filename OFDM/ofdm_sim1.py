# ofdm_sim1.py

import sys, os, time
import numpy as num
import pylab as py
from QAMSources import  Source4QAM,  Source16QAM,  Source32QAM,  Source64QAM,  Source128QAM


# simulation parameters

N           = 1024   # number of subcarriers
L           = 32    # length of cyclic prefix
N_OFDM      = 10000   # number of OFDM symbols
N_sub_ch    = 100   # plot constellation of this subchannel

# normalised frequency offset (df/fs)
f_offset_n = 1.0e-5


#g_channel_impulse = num.array([1, 0.1, -.1, 0.1, .3, -0.04])
g_channel_impulse = num.array([1, 0.0, 0.0, 0.0, .0, 0.0])

G_channel = num.fft.fft(g_channel_impulse, N)

M = len(g_channel_impulse)

overlap_old = num.zeros(M-1)

#error_total = []

sub_channel = num.zeros(N_OFDM, 'D')

t_start = time.clock()
for n_symbol in range(N_OFDM):
    
    # block of 4-QAM symbols
    qam_vec1 = Source16QAM(N/4)
    qam_vec2 = Source16QAM(N/4)
    qam_vec3 = Source16QAM(N/4)
    qam_vec4 = Source16QAM(N/4)
    
    qam_vec = num.concatenate( (qam_vec1, qam_vec2, qam_vec3, qam_vec4) )
    
    # useful part of OFDM symbol (N subcarriers)
    y_vec = N*num.fft.ifft(qam_vec)  # factor N compensates for the internal scaling of function ifft()
    
    # extract cyclic prefix
    cyclic_prefix = y_vec[N-L:]
    
    # prepend cyclic prefix to form the full OFDM symbol
    ofdm_vec = num.concatenate( (cyclic_prefix, y_vec) )
    
    # the channel ...
    r_vec = num.convolve(ofdm_vec, g_channel_impulse)    
    
    # split into vectors r1_vec, r2_vec 
    r1_vec        = r_vec[0:N+L]
    r2_vec        = r_vec[N+L:]
    
    # correct for channel output of last OFDM-symbol
    r1_vec[0:M-1] = r1_vec[0:M-1] + overlap_old
    
    # save overlap part for next ..
    overlap_old = r2_vec
    
    # frequency offset of receiver
    fo_vec = num.exp(2.j *num.pi * f_offset_n * num.arange(N+L)) 
    
    # apply frequency offset
    r1_vec_fo = r1_vec * fo_vec
    
    # discard cyclic prefix part
    ofdm_rec = r1_vec_fo[L:]   # should have N samples otherwise wrong
      
    # transform back
    # correct for scaling
    # correct for frequency dependent gain due to channel distortion
    
    data_rec = (1./ N) * num.fft.fft(ofdm_rec) / G_channel
    
    # deviation of received / sent data symbols
    error = data_rec - qam_vec
    
    # retrieve data of sub-channel Nr. N_sub_ch
    sub_channel[n_symbol] = data_rec[N_sub_ch]
    

# record elapsed time    
t_stop = time.clock()
t_elapsed = t_stop - t_start

print "time elapsed = %10.2f s" % t_elapsed

# some figures ...

# scatter plot of sub-channel Nr. N_sub_ch
py.figure()
py.scatter(sub_channel.real, sub_channel.imag, s=1, c='b')
py.axis('equal')
py.xlabel('I')
py.ylabel('Q')
py.title("constellation of sub-carrier Nr = %d  # N = %d" % (N_sub_ch, N) )
py.grid(True)



py.show()

py.figure()
py.plot(r_vec)
py.show()    
    
    
    
