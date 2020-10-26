import numpy as np
from ctypes import CDLL
from ctypes.util import find_library

# Load librtlsdr library
crtlsdr_shared_lib = "rtlsdr.so"
if find_library(crtlsdr_shared_lib) is None:
    raise ValueError("")
print(find_library("rtlsdr.so"))