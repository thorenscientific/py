from numpy import min, max
from scipy import linspace
from scipy.signal import lti, step

# making transfer function
# example from Ogata Modern Control Engineering 
# 4th edition, International Edition page 307

# num and den, can be list or numpy array type
num = [2] 

#denominator of the form s^2 + s +1
den = [5, 4, 1]

tf = lti(num, den)

# get t = time, s = unit-step response
t, s = step(tf)

# recalculate t and s to get smooth plot
t, s = step(tf, T = linspace(min(t), t[-1], 500))

# get i = impulse
#t, i = impulse(tf, T = linspace(min(t), t[-1], 500))

from matplotlib import pyplot as plt

#plt.plot(t, s, t, i)
plt.plot(t, s)
plt.title('Transient-Response Analysis')
plt.xlabel('Time(sec)')
plt.ylabel('Amplitude')
plt.hlines(1, min(t), max(t), colors='r')
plt.hlines(0, min(t), max(t))
plt.xlim(xmax=max(t))
plt.legend(('Unit-Step Response',), loc=0)
plt.grid()
plt.show()