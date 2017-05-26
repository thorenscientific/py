'''
simplify_LTC2508_filter_files.py

get rid of zeros in Manideep's files


Mark Thoren
Linear Technology Corporation
June, 2015
'''

# First, import goodies from standard libraries
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
import time

start_time = time.time();


ssinc_256 = np.ndarray(2175, dtype=float)
ssinc_1024 = np.ndarray(8703, dtype=float)
ssinc_4096 = np.ndarray(34815, dtype=float)
ssinc_16384 = np.ndarray(139263, dtype=float)

with open('ssinc_256.txt', 'r') as infile:
    for i in range(0, 2175):
        instring = infile.readline()
        ssinc_256[i] = float(instring)
print('done reading DF 256!')


with open('ssinc_1024.txt', 'r') as infile:
    for i in range(0, 8703):
        instring = infile.readline()
        ssinc_1024[i] = float(instring)
print('done reading DF 1024!')

with open('ssinc_4096.txt', 'r') as infile:
    for i in range(0, 34815):
        instring = infile.readline()
        ssinc_4096[i] = float(instring)
print('done reading DF 4096!')

with open('ssinc_16384.txt', 'r') as infile:
    for i in range(0, 139263):
        instring = infile.readline()
        ssinc_16384[i] = float(instring)
print('done reading DF 16384!')

ssinc_256_int = np.rint(ssinc_256)
ssinc_1024_int = np.rint(ssinc_1024)
ssinc_4096_int = np.rint(ssinc_4096)
ssinc_16384_int = np.rint(ssinc_16384)

# Now write out rounded / integerized files

with open('ssinc_256_int.txt', 'w') as outfile:
    for i in range(0, 2175):
        outfile.write(str(int(ssinc_256_int[i]))+"\n")
print('done writing DF 256!')


with open('ssinc_1024_int.txt', 'w') as outfile:
    for i in range(0, 8703):
        outfile.write(str(int(ssinc_1024_int[i]))+"\n")
print('done writing DF 1024!')

with open('ssinc_4096_int.txt', 'w') as outfile:
    for i in range(0, 34815):
        outfile.write(str(int(ssinc_4096_int[i]))+"\n")
print('done writing DF 4096!')

with open('ssinc_16384_int.txt', 'w') as outfile:
    for i in range(0, 139263):
        outfile.write(str(int(ssinc_16384_int[i]))+"\n")
print('done writing DF 16384!')



print "My program took", (time.time() - start_time), " seconds to run"