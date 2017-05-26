# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

def ComputerUnitsToByte(capacity, unit):
    if(unit == "KB"):
        print(capacity * 2**10)
    if(unit == "MB"):
        print(capacity * 2**20)
    if(unit == "G"):
        print(capacity * 2**30)
    if(unit == "TB"):
        print(capacity * 2**40)
    if(unit == "P"):
        print(capacity * 2**50)
    #print "Done"
        
def digitSum(n):
    s = 0
    for digit in range (10):
        d = n%10 # Modulus 10, find digit
        s += d # add sum
        n /=10 # "binary right-shift"
    return s