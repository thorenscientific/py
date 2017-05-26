import FTSyncFifoDevicePy
import time

try:
    ft2232 = FTSyncFifoDevicePy.FTSyncFifoDevice()
    ft2232.OpenByDescription(['LTC UFO Board'])

    ft2232.SetMode(ft2232.ModeFIFO)

    samples_to_read = 1024

    time.sleep(1)

    samples_read, data = ft2232.FIFOReceiveUShorts(samples_to_read)

    print "Read out " + str(samples_read) + " samples"
    print data
finally:
    ft2232.Close() #End of main loop.
print 'Done!'