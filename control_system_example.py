from numpy import min, max
import numpy as np
from scipy import linspace
from scipy.signal import lti, step, impulse, bilinear, dstep
 
# making transfer function
# example from Ogata Modern Control Engineering
# 4th edition, International Edition page 307
 
# num and den, can be list or numpy array type
#Original numerator and denominator from Ortega:
#num = [6.3223, 5, 12.811]
#den = [1, 6, 11.3223, 18, 12.811]

#Suspension model from
#http://www.swarthmore.edu/NatSci/echeeve1/Class/e12/Lectures/XferFunc/html/XferFunc.html
num = [400, 800]
den = [100, 400, 800]

tf = lti(num, den)
print type(tf)
print tf
print "Zeros:"
print tf.zeros
print "Poles:"
print tf.poles
print "Gain:"
print tf.gain



#print tf.num

#print tf.den

#now do a discrete-time version, with a sample rate of 10sps:
discrete_tf = bilinear(num, den, 16)

dnum = discrete_tf[0]
dden = discrete_tf[1]

print "Discrete Xfer function:"
print discrete_tf
print "index 0:"
print discrete_tf[0]
print "index 1:"
print discrete_tf[1]

# get t = time, s = unit-step response
#t, s = step(tf)
print "Let's try to make a time vector:"
T = linspace(0, 5, 100)
print type(T)
print T.shape
#print T


#print "this is 't'"
#print t
#print "this is s"
#print s
 
# recalculate t and s to get smooth plot
#t, s = step(tf, T )
t, s = step(tf, T = linspace(0, 5, 100))
#t, s = step(tf, T)
dsys = (dnum, dden, 1/50.0)
print "dsys type:"
print type(dsys)
dt, ds = dstep(dsys)

print "ds:"
print ds

print "ds type:"

print type(ds)

ds_yvals = np.array(ds[0][0:,0])

#print "continuous time values:"
#print t.shape
#print t

print "discrete time values:"
print dt.shape
print dt

print "extracted discrete y shape and values:"
print ds_yvals.shape
print ds_yvals


# get i = impulse
#t, i = impulse(tf, T = linspace(min(t), t[-1], 500))
#t, i = impulse(tf, T = linspace(0, 10, 500))

#print "And whatever the heck T is:"
#T = linspace(min(t), t[-1], 500)
#print type(T)
#print T
 
from matplotlib import pyplot as plt
figure(1)
plt.subplot(211)
plt.plot(dt, ds[0])
plt.subplot(212)
plt.plot(dt, ds_yvals)
plt.title('Transient-Response Analysis')
plt.xlabel('Time(sec)')
plt.ylabel('Amplitude')
plt.hlines(1, min(t), max(t), colors='r')
plt.hlines(0, min(t), max(t))
plt.xlim(xmax=max(t))
plt.legend(('Unit-Step Response', 'Unit-Impulse Response'), loc=0)
plt.grid()
plt.show()
