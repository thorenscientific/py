'''
simplify_all_LTC2500_filter_files.py

Process Manideep's filter coefficient files:
Strip trailing zeros from integers
Append trailing zero coefficients to match leading zero coefficients.
Generate SINC filters from scratch, with a leading and trailing zero coeff.

Mark Thoren
Linear Technology Corporation
June, 2015
'''

# First, import goodies from standard libraries
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
import time

def linecount(fname): # A handy functon to count lines in a file.
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

# List of downsample factors
dfs = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]


start_time = time.time() # See how long program takes to run.

# First, ssinc files. Original files have lots of zeros after the decimal point,
# and the occasional xxx.99999, xxx.000001 that need to be RINT-ed.
# Also, append trailing zeros for symmetry.
print ("Processing SSINC filters...")
for df in dfs:
    inf = "ssinc_" + str(df) + ".txt"
    outf = "output/ssinc_" + str(df) + ".txt"
    length = linecount(inf)
    ssinc_x = np.ndarray(length, dtype=float)
    leadingzeros = 0
    foundnonzero = False
    with open(inf, 'r') as infile:
        for i in range(0, length):
            instring = infile.readline()
            ssinc_x[i] = float(instring)
    print('done reading DF ' + str(df) + '!')
            
    ssinc_x_int = np.rint(ssinc_x) #round to nearest integer
    
    with open(outf, 'w') as outfile:
        for i in range(0, length):
            if((ssinc_x_int[i] == 0) & (foundnonzero == False)):
                leadingzeros += 1
            else:
                foundnonzero = True
            outfile.write(str(int(ssinc_x_int[i]))+"\n")
        print("Found this many leading zeros:" + str(leadingzeros))
        for i in range(0, leadingzeros):
            outfile.write(str(0))
            if i < (leadingzeros-1):
                outfile.write("\n")
        print('done writing DF ' + str(df) + '!')


# SSINC+Flattening filter files. These ARE floating point numbers, the only
# thing that needs to be done is to append zeros to the end.
print ("Processing SSINC + Flattening filters...")
for df in dfs:
    inf = "ssinc_flat_" + str(df) + ".txt"
    outf = "output/ssinc_flat_" + str(df) + ".txt"
    length = linecount(inf)
    ssinc_flat_x = []
    leadingzeros = 0
    foundnonzero = False
    with open(inf, 'r') as infile:
        for i in range(0, length):
            instring = infile.readline()
            ssinc_flat_x.append(instring.strip()) # Strip newlines
    print('done reading DF ' + str(df) + '!')

    with open(outf, 'w') as outfile:
        for i in range(0, length):
            if((float(ssinc_flat_x[i]) == 0.0) & (foundnonzero == False)):
                leadingzeros += 1
            else:
                foundnonzero = True
            outfile.write(str(ssinc_flat_x[i])+"\n")
        print("Found this many leading zeros:" + str(leadingzeros))
        for i in range(0, leadingzeros):
            outfile.write("0.000000")
            if i < (leadingzeros-1):
                outfile.write("\n")
        print('done writing DF ' + str(df) + '!')
        
        
# SINC filters now...
print("Generating SINC filters...")
for df in dfs:
    sinc1 = np.ones(df)
    sinc2 = np.convolve(sinc1, sinc1)
    sinc3 = np.convolve(sinc1, sinc2)
    sinc4 = np.convolve(sinc2, sinc2)
    
    with open("output/sinc1_" + str(df) + ".txt", "w") as outfile:
        outfile.write("0\n") # A single leading zero...
        for i in range(0, len(sinc1)):
            outfile.write(str(int(sinc1[i]))+"\n")
        outfile.write("0") # A single trailing zero...

    with open("output/sinc2_" + str(df) + ".txt", "w") as outfile:
        outfile.write("0\n") # A single leading zero...
        for i in range(0, len(sinc2)):
            outfile.write(str(int(sinc2[i]))+"\n")
        outfile.write("0") # A single trailing zero...
        
    with open("output/sinc3_" + str(df) + ".txt", "w") as outfile:
        outfile.write("0\n") # A single leading zero...
        for i in range(0, len(sinc3)):
            outfile.write(str(int(sinc3[i]))+"\n")
        outfile.write("0") # A single trailing zero...    

    with open("output/sinc4_" + str(df) + ".txt", "w") as outfile:
        outfile.write("0\n") # A single leading zero...
        for i in range(0, len(sinc4)):
            outfile.write(str(int(sinc4[i]))+"\n")
        outfile.write("0") # A single trailing zero...

print "My program took", (time.time() - start_time), " seconds to run"