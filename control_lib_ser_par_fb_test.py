# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 17:43:03 2014

@author: mark_t
"""

# A simple integrator transfer function with a discrete time step of 1.0 could be implemented as:

from scipy import signal
import control

tf = ([1.0,], [1.0, -1.0], 1.0)
t_in = [0.0, 1.0, 2.0, 3.0]
u = np.asarray([0.0, 0.0, 1.0, 1.0])
t_out, y = signal.dlsim(tf, u, t=t_in)

print "tf: "
print tf

#num = [[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]]
#den = [[[9., 8., 7.], [6., 5., 4.]], [[3., 2., 1.], [-1., -2., -3.]]]

num = [1]
den = [1, 1]
sys1 = control.tf(num, den)
 

print "tf in series with tf: "
print control.series(sys1, sys1)

print "tf in parallel with tf: "
print control.parallel(sys1, sys1)

print "tf in feedback with tf: "
print control.feedback(sys1, sys1)