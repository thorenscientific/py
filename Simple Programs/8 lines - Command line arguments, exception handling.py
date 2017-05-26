#8 lines - Command line arguments, exception handling

#!/usr/bin/env python
# This program adds up integers in the command line
import sys


#Cool trick to set command line args directly
try:
    __file__  # "___file___" is quite literally, the name of this file
    print "The name of this file is: ", ___file___, "and that is that"

except:
    sys.argv = [sys.argv[0], 4, 5, 6]


try:
    total = sum(int(arg) for arg in sys.argv[1:])
    print 'sum =', total
except ValueError:
    print 'Please supply integer arguments'
