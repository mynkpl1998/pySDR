import numpy as np
from ctypes import CDLL, c_int32, c_ubyte, POINTER, c_uint32, c_int
from ctypes.util import find_library
from pysdr.utils import print_error_msg, c_ubyte_ptr_to_string

class librtlsdr:

    """
    Responsible for loading the c rtlsdr shared object library. 
    The librtlsdr must be installed on the system.
    The installation can be done by following the 
    instructions from https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr.

    Raises
    ------
        * ValueError:
                                * If the librtlsdr is not found on the system.
    
    Attributes
    ----------

    * clib:                     Returns the CDLL library object of the librtlsdr.
    """

    def __init__(self, ):
        
        # Load librtlsdr library
        crtlsdr_shared_lib = 'rtlsdr.so'
        if find_library(crtlsdr_shared_lib) is None:
            print_error_msg("Unable to find librtlsdr.so. Make sure to install it from https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr.")
            raise ValueError

        self.__clib = CDLL("lib" + crtlsdr_shared_lib)

        # API's init status
        self.__apis_init_stat = {}
        for api_name in dir(librtlsdr):
            if "py_rtlsdr" in api_name:
                self.__apis_init_stat[api_name] = False
    
    @property
    def clib(self):
        return self.__clib
    
    def py_rtlsdr_get_device_count(self,):
        """
        Returns the number of RTL-SDR devices
        connected to the host.
        """
        if not self.__apis_init_stat['py_rtlsdr_get_device_count']:
            f = self.clib.rtlsdr_get_device_count
            f.restype, f.argstypes = c_uint32, []
            self.__apis_init_stat['py_rtlsdr_get_device_count'] = True
        return self.clib.rtlsdr_get_device_count()
    
    def py_rtlsdr_get_device_name(self, device_index=0):
        """
        Returns the name of the connected device at
        given index.

        Parameters
        ----------
        * device_index:                      Device index.

        Raises
        ------
        * ValueError
                                    * If device index is greater than 
                                    the number of connected devices.
                                    * If device index is negative.
        """

        if not self.__apis_init_stat['py_rtlsdr_get_device_name']:
            f = self.clib.rtlsdr_get_device_name
            f.restype, f.argstypes = POINTER(c_ubyte), [c_uint32]
            self.__apis_init_stat['py_rtlsdr_get_device_name'] = True
        
        self.__check_for_rtlsdr_devices()
        
        if device_index < 0:
            print_error_msg("Device index must be non-negative.")
            raise ValueError
        
        if device_index >= self.py_rtlsdr_get_device_count():
            print_error_msg("Expected device index < %d. Got device index: %d."%(self.py_rtlsdr_get_device_count(), device_index))
            raise ValueError

        device_name = self.clib.rtlsdr_get_device_name(c_uint32(device_index))
        return c_ubyte_ptr_to_string(device_name, 126)
    
    def __check_for_rtlsdr_devices(self):
        """
        Checks whether any RTL-SDR device
        is attached to the host.

        Raises
        ------
        * ValueError                    : No device is found.
        """
        if self.py_rtlsdr_get_device_count() == 0:
            print_error_msg("No RTL-SDR device is attached to the host.")
            raise ValueError
      
    def py_rtlsdr_get_device_usb_strings(self, device_index=0):
        """
        Returns the USB device strings.

        Parameters
        ----------
        * device_index                  : Device index.

        Returns
        -------
        * mid                           : Device manufacturer.
        * pid                           : Device product ID.
        * serial                        : Device serial ID.

        Raises
        ------
        * TypeError
                                        * If device index is negative.
                                        * If device index is greater than or
                                        equal to the number of connected 
                                        supported devices.
        """
        if not self.__apis_init_stat['py_rtlsdr_get_device_usb_strings']:
            f = self.clib.rtlsdr_get_device_usb_strings
            f.restype, f.argstypes = c_int, [c_uint32, POINTER(c_ubyte), POINTER(c_ubyte), POINTER(c_ubyte)]
            self.__apis_init_stat['py_rtlsdr_get_device_usb_strings'] = True
        
        self.__check_for_rtlsdr_devices()

        if device_index < 0:
            print_error_msg("Device index must be non-negative.")
            raise ValueError
        
        if device_index >= self.py_rtlsdr_get_device_count():
            print_error_msg("Expected device index < %d. Got device index: %d."%(self.py_rtlsdr_get_device_count(), device_index))
            raise ValueError

        mid = (c_ubyte * 256)()
        pid = (c_ubyte * 256)()
        serial = (c_ubyte * 256)()
        result = self.clib.rtlsdr_get_device_usb_strings(c_uint32(device_index),
                                                          mid,
                                                          pid,
                                                          serial)
        if(result != 0):
            print_error_msg("Failed tp fetch USB device strings for device indexed as %d."%(device_index))
            raise ValueError
        return c_ubyte_ptr_to_string(mid, 256), c_ubyte_ptr_to_string(pid, 256), c_ubyte_ptr_to_string(serial, 256)