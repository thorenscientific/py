#Usage : python setup*.py py2exe --includes sip

from distutils.core import setup
import py2exe
import matplotlib

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.3.3",
    description = "pyPIDTune stand alone exe",
    name = "pyPIDTune",
    # matplot lib
    data_files = matplotlib.get_py2exe_datafiles(),
    options = {'py2exe': {'excludes': ['_gtkagg', '_tkagg']}},
    # targets to build
    windows = ['pyPIDTune.py']
    )
