from pysdr.rtlsdr import *

def test_librtlsdr_initialization():

    """
    Verifies the librtlsdr intialization.
    This test is aim to test successful loading
    of librtlsdr.so library.
    """
    obj = librtlsdr()
