# QAMSources.py

"""
21.12.2007
m. biester

"""

import sys, os
import numpy as num

ph4_rot = num.array([1, 1j, -1, -1j])

qam4_1q = num.array([1+1j])

qam16_1q = num.array([1+1j, 3+1j, 1+3j, 3+3j])

qam32_1q = num.array([1+1j, 3+1j, 5+1j, 1+3j, 3+3j, 5+3j, 1+5j, 3+5j])

qam64_1q = num.array([1+1j, 3+1j, 5+1j, 7+1j,\
                      1+3j, 3+3j, 5+3j, 7+3j,\
                      1+5j, 3+5j, 5+5j, 7+5j,\
                      1+7j, 3+7j, 5+7j, 7+7j])

qam128_1q = num.array([1+1j,  3+1j,  5+1j,  7+1j, 9+1j, 11+1j,\
                       1+3j,  3+3j,  5+3j,  7+3j, 9+3j, 11+3j,\
                       1+5j,  3+5j,  5+5j,  7+5j, 9+5j, 11+5j,
                       1+7j,  3+7j,  5+7j,  7+7j, 9+7j, 11+7j,\
                       1+9j,  3+9j,  5+9j,  7+9j,\
                       1+11j, 3+11j, 5+11j, 7+11j ])

qam256_1q = num.array([1+1j,  3+1j,  5+1j,  7+1j,  9+1j,  11+1j,  13+1j,  15+1j,\
                       1+3j,  3+3j,  5+3j,  7+3j,  9+3j,  11+3j,  13+3j,  15+3j,\
                       1+5j,  3+5j,  5+5j,  7+5j,  9+5j,  11+5j,  13+5j,  15+5j,\
                       1+7j,  3+7j,  5+7j,  7+7j,  9+7j,  11+7j,  13+7j,  15+7j,\
                       1+9j,  3+9j,  5+9j,  7+9j,  9+9j,  11+9j,  13+9j,  15+9j,\
                       1+11j, 3+11j, 5+11j, 7+11j, 9+11j, 11+11j, 13+11j, 15+11j,\
                       1+13j, 3+13j, 5+13j, 7+13j, 9+13j, 11+13j, 13+13j, 15+13j,\
                       1+15j, 3+15j, 5+15j, 7+15j, 9+15j, 11+15j, 13+15j, 15+15j])


def Source4QAM(block_len):
    """
    block_len  : nr of 4-QAM symbols in block
                
    returns    
    
    qam4_array : complex numpy array with block_len 4 QAM symbols
    """
    # random index vector for quadrant selection
    iquad = num.random.randint(0, 4, block_len)
    
    # random index vector for selection of symbol(s) from 1st quadrant
    isymbol = num.zeros(block_len, 'L') # with 4-QAM only 1 symbol per quadrant
    
    qam4_array = ph4_rot[iquad] * qam4_1q[isymbol]
    return qam4_array

def Source16QAM(block_len):
    """
    block_len  : nr of 16-QAM symbols in block
                
    returns    
    
    qam16_array : complex numpy array with block_len 16 QAM symbols
    """
    # random index vector for quadrant selection
    iquad = num.random.randint(0, 4, block_len)
    
    # random index vector for selection of symbol(s) from 1st quadrant
    N_symbols = len(qam16_1q) # nr of symbols in quadrant
    isymbol   = num.random.randint(0, N_symbols, block_len)
    
    qam16_array = ph4_rot[iquad] * qam16_1q[isymbol]
    return qam16_array

def Source32QAM(block_len):
    """
    block_len  : nr of 32-QAM symbols in block
                
    returns    
    
    qam32_array : complex numpy array with block_len 32 QAM symbols
    """
    # random index vector for quadrant selection
    iquad = num.random.randint(0, 4, block_len)
    
    # random index vector for selection of symbol(s) from 1st quadrant
    N_symbols = len(qam32_1q) # nr of symbols in quadrant
    isymbol   = num.random.randint(0, N_symbols, block_len)
    
    qam32_array = ph4_rot[iquad] * qam32_1q[isymbol]
    return qam32_array

def Source64QAM(block_len):
    """
    block_len  : nr of 64-QAM symbols in block
                
    returns    
    
    qam64_array : complex numpy array with block_len 64 QAM symbols
    """
    # random index vector for quadrant selection
    iquad = num.random.randint(0, 4, block_len)
    
    # random index vector for selection of symbol(s) from 1st quadrant
    N_symbols = len(qam64_1q)  # nr of symbols in quadrant
    isymbol   = num.random.randint(0, N_symbols, block_len)
    
    qam64_array = ph4_rot[iquad] * qam64_1q[isymbol]
    return qam64_array

def Source128QAM(block_len):
    """
    block_len  : nr of 128-QAM symbols in block
                
    returns    
    
    qam128_array : complex numpy array with block_len 128 QAM symbols
    """
    # random index vector for quadrant selection
    iquad = num.random.randint(0, 4, block_len)
    
    # random index vector for selection of symbol(s) from 1st quadrant
    N_symbols = len(qam128_1q) # nr of symbols in quadrant
    isymbol   = num.random.randint(0, N_symbols, block_len)
    
    qam128_array = ph4_rot[iquad] * qam128_1q[isymbol]
    return qam128_array

def Source256QAM(block_len):
    """
    block_len  : nr of 256-QAM symbols in block
                
    returns    
    
    qam256_array : complex numpy array with block_len 256 QAM symbols
    """
    # random index vector for quadrant selection
    iquad = num.random.randint(0, 4, block_len)
    
    # random index vector for selection of symbol(s) from 1st quadrant
    N_symbols = len(qam256_1q) # nr of symbols in quadrant
    isymbol   = num.random.randint(0, N_symbols, block_len)
    
    qam256_array = ph4_rot[iquad] * qam256_1q[isymbol]
    return qam256_array