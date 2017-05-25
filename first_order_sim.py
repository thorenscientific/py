# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 09:11:25 2014

@author: mark_t
"""

#This script simulates a discrete control system

#from control.matlab import *
import numpy as np
import control
from scipy import linspace
from scipy.signal import dstep
from matplotlib import pyplot as plt

Ts = 0.1
Tclk = 10

#system time constant
tau = 12800e-9

#PID parameters
Kp = 4.0
Ki = 0.5
Kd = 0.1

#setpoint
setpoint = 10000.0

#round to nearest fixed point values for model
fp_res = 8.0
fp_bits = 16.0

tau_fp = round((tau/Ts)*pow(2.0,fp_res)/pow(2.0, fp_res))

if(tau_fp > 2 ** fp_bits):
    print 'error. floating point bit width too small'
elif(tau_fp == 0):
    print'error. floating point resolution too small'


tau_err = (tau_fp-tau/Ts)/(tau/Ts)

tau_gain = 1/(1+tau/Ts);
tau_gain_fp = round(tau_gain * 2 ** fp_res/pow(2, fp_res))
if(tau_gain_fp > 2 ** fp_bits):
    print'error. floating point bit width too small'
elif(tau_gain_fp == 0):
    print 'error. floating point resolution too small'


tau_gain_err = (tau_gain_fp-tau_gain)/tau_gain

#calculate actual PID constants
pid_fp_res = 8.0
pid_fp_bits = 16.0
kp_fp = round(Kp*2**pid_fp_res)/2**pid_fp_res
ki_fp = round((Ki*Ts)*2**pid_fp_res)/2**pid_fp_res/Ts
kd_fp = round((Kd/Ts)*2**pid_fp_res)/2**pid_fp_res*Ts

#kp_err = (kp_fp-Kp)/Kp
#ki_err = (ki_fp-Ki)/Ki
#kd_err = (kd_fp-Kd)/Kd

#create ideal first order model
hz = control.matlab.tf([Tclk, 0], [(Tclk + tau), -tau], Tclk)

hz2 = control.matlab.tf([0.0016,0.0062], [1,-0.9922], Ts) #From matlab output from d2d...
#hz2 = control.matlab.tf([1], [1, 0], Ts)
#create PID with no derivative filter
#ctrl = pid(Kp, Ki, Kd, 0, Ts)

p_tf = control.matlab.tf([Kp], [1], Ts)
i_tf = control.matlab.tf([Ki], [1, 0], Ts)
d_tf = control.matlab.tf([Kd, 0], [0, 1], Ts)

asdf = control.matlab.parallel(p_tf, i_tf)
pid = asdf#control.matlab.parallel(asdf, d_tf)

feedforward = control.matlab.series(pid, hz2)
feedback = control.matlab.tf(1, 1, Ts)

#ctrl = control.tf(1, [1, 0], Ts)


delay = control.matlab.tf(1, [1, 0], Ts)
print "delay's type: "
print type(delay)

T_ideal = control.matlab.feedback(feedforward, feedback, Ts)
#T_ideal = control.matlab.tf([1], [1, -.9], Ts)

print "\nclosed loop xfer function:"
print T_ideal
print "\nxfer f'n's type:"
print type(T_ideal)
print "\nxfer f'n's vars:"
print vars(T_ideal)
print "\nxfer f'n's num:"
num = T_ideal.num[0][0]
print T_ideal.num
print "\nxfer f'n's den:"
den = T_ideal.den[0][0]
print T_ideal.den
print "\nxfer f'n's dt:"
print T_ideal.dt

print "\nxfer f'n's poles"
print control.matlab.pole(T_ideal)

print "\nxfer f'n's DC gain"
print control.matlab.dcgain(T_ideal)


#T_ideal_tf = (num, den, T_ideal.dt)#control.tf(T_ideal.num, T_ideal.den, T_ideal.dt)
#T_ideal_tf = control.matlab.tf(T_ideal)

T = np.linspace(0, 500, 1000)


#T, y = control.matlab.step(T_ideal, T = np.linspace(0, 100, 500), input=0, output=0)#, T=None, input=0, output=0)

dsys = (num, den, Ts)
print "Dsys:"
print dsys
T, y = dstep(dsys, t=T)#, T=None, input=0, output=0)



plt.figure(1)
plt.plot(T, y[0])
plt.show()



#create implemented model
#hz_actual = tf([tau_gain_fp, 0], [1, -tau_gain_fp*tau_fp], Ts)
#create PID with no derivative filter
#ctrl_actual = pid(kp_fp, ki_fp, kd_fp, 0, Ts)
"""
T_actual = control.matlab.feedback(ctrl_actual*delay*hz_actual, 1)


plt.figure(2)
plt.plot(control.matlab.step(T_actual))
plt.show()
"""
