# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:30:21 2013

@author: elbar
"""

from numpy import polyadd, polymul
from scipy import signal

#-------------------------------------------------------------------------------
class TransferFunction():
    ''' transfer function and var useful utils '''
    
    def __init__(self, num=[1], den=[1], delay=0.0, pade_order=1):
        ''' init vars '''
        self.lti = None
        self.num = num
        self.den = den        
        self.delay = delay
        self.pade_order = pade_order
        self.is_FODT = False
        self.k_FODT = 0.0
        self.t_FODT = 0.0
        self._build_tf()

    def _build_tf(self):
        ''' build transfer function '''
        self._tf = signal.lti(self.num, self.den)
        self._tf_pade_delay = pade_lti(self.delay, self.pade_order)
        self.lti = mul_lti(self._tf, self._tf_pade_delay)

    def set_lti(self, lti):
        ''' change transfer function directly'''
        self.num = lti.num
        self.den = lti.den
        self._build_tf()

    def bode(self):
        ''' bode return values '''
        return self.lti.bode()
    
    def step(self):
        ''' step response return values '''
        return self.lti.step()    

    def impulse(self):
        ''' impulse response return values '''
        return self.lti.impulse()

    def nyquist(self):
        ''' nyquist response return values '''
        return self.lti.freqresp()

    def __str__(self):
        ''' transfer function string representation '''
    
        out_str = ""
        # Convert the numerator and denominator polynomials to strings.
        num_str = self._tf_poly_to_str(self.num)
        den_str = self._tf_poly_to_str(self.den)
        # Figure out the length of the separating line
        dash_count = max(len(num_str), len(den_str))
        dashes = '-' * dash_count
        # Center the numerator or denominator
        if len(num_str) < dash_count:
            num_str = (' ' * int(round((dash_count - len(num_str))/2)) + 
                num_str)
        if len(den_str) < dash_count: 
            den_str = (' ' * int(round((dash_count - len(den_str))/2)) + 
                den_str)
    
        out_str += "\n" + num_str + "\n" + dashes + "\n" + den_str + "\n"
    
        return out_str
        
    def _tf_poly_to_str(self, coeffs, var='s'):
        """Convert a transfer function polynomial to a string"""
    
        out_str = "0"
        
        # Compute the number of coefficients
        N = len(coeffs)-1
        
        for k in range(len(coeffs)):
            coef_str ='%.4g' % abs(coeffs[k])
            if coef_str[-4:] == '0000':
                coef_str = coef_str[:-5]
            power = (N-k)
            if power == 0:
                if coef_str != '0':
                    new_str = '%s' % (coef_str,)
                else:
                    if k == 0:
                        new_str = '0'
                    else:
                        new_str = ''
            elif power == 1:
                if coef_str == '0':
                    new_str = ''
                elif coef_str == '1':
                    new_str = var
                else:
                    new_str = '%s %s' % (coef_str, var)
            else:
                if coef_str == '0':
                    new_str = ''
                elif coef_str == '1':
                    new_str = '%s^%d' % (var, power,)
                else:
                    new_str = '%s %s^%d' % (coef_str, var, power)
        
            if k > 0:
                if new_str != '':
                    if coeffs[k] < 0:
                        out_str = "%s - %s" % (out_str, new_str)
                    else:
                        out_str = "%s + %s" % (out_str, new_str)
            elif (k == 0) and (new_str != '') and (coeffs[k] < 0):
                out_str = "-%s" % (new_str,)
            else:
                out_str = new_str
        
        return out_str
        
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def pade_lti(delay, n=1):
    ''' 
    Create a linear system that approximates a delay.
    
    Return the lti object of the Pade approximation.
    
    Parameters
    ----------
    t : time delay in sec
    n : order of approximation
        
    Returns
    -------       
    num, den : array
        Polynomial coefficients of the delay model, in descending powers of s.
    
    Notes
    -----
    Based on an algorithm in Golub and van Loan, "Matrix Computation" 3rd.
    Ed. pp. 572-574.
    '''
    
    if delay == 0:
        num = [1,]
        den = [1,]
    else:
        num = [0. for i in range(n+1)]
        num[-1] = 1.
        den = [0. for i in range(n+1)]
        den[-1] = 1.
        c = 1.
        for k in range(1, n+1):
            c = delay * c * (n - k + 1)/(2 * n - k + 1)/k
            num[n - k] = c * (-1)**k
            den[n - k] = c 
        num = [coeff/den[0] for coeff in num]
        den = [coeff/den[0] for coeff in den]
    
    return signal.lti(num, den) 
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def mul_lti(sys1, sys2):
    ''' multiply sys1 and sys2 LTI objects 
        returns sys1 * sys2    
    '''
    num1 = sys1.num
    den1 = sys1.den
    num2 = sys2.num
    den2 = sys2.den
    num = polymul(num1, num2)
    den = polymul(den1, den2)
    return signal.lti(num, den)

#-------------------------------------------------------------------------------        

#-------------------------------------------------------------------------------
def feedback_lti(sys1, sys2, sign=-1):
    ''' Feedback interconnection between sys1 and sys2 LTI objects 
        returns sys1 / (1 - sign * sys1 * sys2)    
    '''
    num1 = sys1.num
    den1 = sys1.den
    num2 = sys2.num
    den2 = sys2.den
    num = polymul(num1, den2)
    den = polyadd(polymul(den2, den1), -sign * polymul(num2, num1))
    return signal.lti(num, den)

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def closed_loop_lti(sys, pid):
    ''' Closed lopp LTI 
        returns sys * pid / (1 + sys * pid)    
    '''
    num1 = sys.num
    den1 = sys.den
    num2 = pid.num
    den2 = pid.den
    num = polymul(num1, num2)
    den = polyadd(polymul(den1, den2), polymul(num1, num2))
    return signal.lti(num, den)

#-------------------------------------------------------------------------------