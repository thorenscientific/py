
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt



#from scipy import *
#import numpy as np
#import matplotlib.pyplot as plt

qam_vec=sp.Source4QAM(1024)

a=sp.zeros(1000)
a[0:100]=1
b = a#convolve(a, a, mode='same')
c=abs(sp.fft(a))


plt.plot(b)

#plt.plot(c)

plt.show()
