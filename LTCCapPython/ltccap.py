# ltccap - a module which uses ctypes to wrap the ltccap.dll for use within python.
#

#imports
import ctypes               # to call the native library
from paramsDialog import *  # for the dialog to enter parameters interactively
import os.path              # for getting the folder from the module path

# Constants

# device
DC718 = 0
DC890 = 1
# bipolarity
BIPOLAR	 = 1
UNIPOLAR = 0
# clock edge
POS_EDGE = 1
NEG_EDGE = 0
# FPGA load IDs
NONE  = 0 # NONE
CMOS  = 1 # CMOS
LVDS  = 2 # LVDS
S1407 = 3 # Deserializer 1407 class
S1408 = 4 # Deserializer 1408 class
S2308 = 5 # Deserializer 2308 class
S2366 = 6 # Deserializer 2366 class
DCMOS = 7 # DDR CMOS
DLVDS = 8 # DDR LVDS
#  trigger modes
IMMEDIATE = 0 # immediate start
POS_START = 1 # start on positive edge
NEG_START = 2 # start on negative

class LtcCap():

    @staticmethod
    def create(device, nChannels, nBits, alignment, isBipolar, clockEdge, fpgaLoad):
        """Create an LtcCap object, passing in the parameters directly"""
        return LtcCap(device, nChannels, nBits, alignment, isBipolar, clockEdge, fpgaLoad)
    @staticmethod
    def createFromDialog():
        """Create an LtcCap object, getting parameters from a dialog box"""
        root = Tk()
        root.withdraw()
        dlg = ParamsDialog(root)
        root.destroy()
        if not dlg.result:
            raise LtcCapError("User cancelled parameter selection")
        return LtcCap(*dlg.values())

    def read(self, nSamps, trig):
        """call correct native LtcCap### and marshall arrays, note that this method
        allocates the memory to store the data so you don't have to."""
        # set up the arrays
        pData1 = ctypes.c_int * nSamps
        data1  = pData1()
        if self.nChannels == 2:
            pData2 = ctypes.c_int * nSamps
            data2  = pData2()
        else:
            data2 = None

        # read the data
        if self.device == DC718:
            err = self.dll.LtcCap718(nSamps, trig, data1, data2)
        else:
            err = self.dll.LtcCap890(nSamps, trig, data1, data2)
        if err != 0:
            raise LtcCapError(self.dll.LtcGetErr(err).decode("utf-8"))

        if data2 is None:
            return data1
        else:
            return (data1, data2)

    def __init__(self, device, nChannels, nBits, alignment, isBipolar, clockEdge, fpgaLoad):           
        """Don't call this constructor directly, use the create methods above, this sets the
        parameters and loads and initializes the library"""
        # load the library
        library = 'ltccap.dll'
        path = os.path.dirname(__file__)
        try:
            # look in bin folder, above Bindings folder
            lib = os.path.join(path, "../../../bin", library)
            self.dll = ctypes.windll.LoadLibrary(lib)
        except WindowsError:
            try:
                # look next to module
                lib = os.path.join(path, library)
                self.dll = ctypes.windll.LoadLibrary(lib)
            except WindowsError:
                # look in current directory
                self.dll = ctypes.windll.LoadLibrary(library)
        # setup the error function to return strings
        self.dll.LtcGetErr.restype = ctypes.c_char_p
        # initialize the part
        err = self.dll.LtcDevInfo(nChannels, nBits, alignment, isBipolar, clockEdge, fpgaLoad)
        if err != 0:
            raise LtcCapError(self.dll.LtcGetErr(err).decode("utf-8"))

        # these should be read only for user convenience, changing them has no effect
        self.device    = device
        self.nChannels = nChannels
        self.nBits     = nBits
        self.alignment = alignment
        self.isBipolar = isBipolar
        self.clockEdge = clockEdge
        self.fpgaLoad  = fpgaLoad

class LtcCapError(Exception):
    """Exception class for LtcCap errors"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
