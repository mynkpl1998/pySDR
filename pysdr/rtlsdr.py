import numpy as np
from ctypes import CDLL, c_int32, c_ubyte, POINTER, c_uint32, c_int, c_void_p, c_uint, c_void_p, byref
from ctypes.util import find_library
from pysdr.utils import print_error_msg, c_ubyte_ptr_to_string, cstr, print_warn_msg, print_info_msg

"""
Re-defines the c_void_p as the
device handle.
"""
p_rtlsdr_dev = c_void_p

class librtlsdr:

    """
    Responsible for loading the rtlsdr shared library. 
    The librtlsdr must be installed on the system.
    The installation can be done by following the 
    instructions from https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr.

    Raises
    ------
        * ValueError:
                                * If the librtlsdr is not found on the system.
    
    Attributes
    ----------
    * clib                          : Returns the CDLL library object of the librtlsdr.
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
        * device_index              : (int) Device index.

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
        
        if int(device_index) != device_index:
            print_error_msg("Expected device index to be int. Got: %d"%(type(device_index)))
            raise ValueError
    
        device_index = int(device_index)

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
        * device_index                  : (int) Device index.

        Returns
        -------
        * mid                           : (str) Device manufacturer.
        * pid                           : (str) Device product ID.
        * serial                        : (str) Device serial ID.

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

        if int(device_index) != device_index:
            print_error_msg("Expected device index to be int. Got: %d"%(type(device_index)))
            raise ValueError
    
        device_index = int(device_index)

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
    
    def py_rtlsdr_get_index_by_serial(self, serial_id):
        """
        Returns the device index with whose serial number
        is given by serial_id.

        Parameters
        ----------
        * serial_id                     : (str) The serial id of the RTL-SDR device.

        Returns
        -------
        * device_index                  : (int) Returns the device index of the RTL-SDR 
                                            device with serial_id.
        
        Raises
        ------
        * ValueError:
                                        * If serial_id is not string.
        * Warning:
                                        * If not device is found corresponding
                                            to device index.
        """
        
        if not self.__apis_init_stat['py_rtlsdr_get_index_by_serial']:
            f = self.clib.rtlsdr_get_index_by_serial
            f.restype, f.argstypes = c_int, [POINTER(c_ubyte)]
            self.__apis_init_stat['py_rtlsdr_get_index_by_serial'] = True

        self.__check_for_rtlsdr_devices()        

        if type(serial_id) != str:
            print_error_msg("Expected serial_id to be string. Got: %s"%(type(serial_id)))
            raise ValueError
        
        cserial_id = cstr(serial_id)
        result = self.clib.rtlsdr_get_index_by_serial(cserial_id)
        if(result < 0):
            print_warn_msg("Failed to fetch any device with serial id: %s"%(serial_id))
            return None
        return result
    
    def py_rtlsdr_open(self, device_index):
        """
        Create and return the device handle 
        for the RTL-SDR for given device index.

        Parameters
        ----------
        * device_index                      : (int) RTL-SDR device index.

        Raises
        ------
        * ValueError
                                            * If invalid device index is passed.
                                            * If fail to open the device handle.
        
        Returns 
        -------
        * handle                     : (p_rtlsdr_dev) Device handle.
        """

        if not self.__apis_init_stat['py_rtlsdr_open']:
            f = self.clib.rtlsdr_open
            f.restype, f.argtypes = c_int, [POINTER(p_rtlsdr_dev), c_uint]
            self.__apis_init_stat['py_rtlsdr_open'] = True

        self.__check_for_rtlsdr_devices()

        if int(device_index) != device_index:
            print_error_msg("Expected device index to be int. Got: %d"%(type(device_index)))
            raise ValueError
    
        device_index = int(device_index)

        if device_index < 0:
            print_error_msg("Device index must be non-negative.")
            raise ValueError
        
        if device_index >= self.py_rtlsdr_get_device_count():
            print_error_msg("Expected device index < %d. Got device index: %d."%(self.py_rtlsdr_get_device_count(), device_index))
            raise ValueError
        
        dev_p = p_rtlsdr_dev(None)
        c_device_index = c_uint(device_index)
        result = self.clib.rtlsdr_open(dev_p, c_uint(device_index))
        
        if result == -1:
            print_error_msg("Device or libusb is inaccessible.")
            raise ValueError
        
        if result == -3:
            print_error_msg("Device permissions don't fit. Check if dev rules file is installed.")
        
        if(result < 0):
            print_error_msg("Failed to open device handle for device index: %d."%(device_index.value))
            raise ValueError
        return dev_p
    
    def py_rtlsdr_close(self, dev_handle_ptr):
        """
        Closes the existing device handle 
        to a RTL-SDR device.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.

        Raises
        ------
        * ValueError
                                                * If fails to close the device handle.
        
        """

        if not self.__apis_init_stat['py_rtlsdr_close']:
            f = self.clib.rtlsdr_close
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev]
            self.__apis_init_stat['py_rtlsdr_close'] = True

        self.__check_for_rtlsdr_devices()

        result = self.clib.rtlsdr_close(dev_handle_ptr)
        if result != 0:
            print_error_msg("Failed to close device handle for device index: %d."%(device_index))
            raise ValueError

    def py_rtlsdr_get_xtal_freq(self, device_handle_ptr):
        """
        Reads and returns the crystal frequency used to
        clock the RTL2832 and the Rafael Micro R820T tuner.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.

        Returns
        -------
        * rtl_freq                              : (int) Returns RTL2832 crystal frequency in Hz.
        * tuner_freq                            : (int) Returns Tuner frequency in Hz.
       
        Raises
        ------
        * ValueError
                                                * If fails to read the xtal freq of tuner or
                                                    RTL2832 chip.
        
        """

        if not self.__apis_init_stat['py_rtlsdr_get_xtal_freq']:
            f = self.clib.rtlsdr_get_xtal_freq
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev, POINTER(c_uint32), POINTER(c_uint32)]
            self.__apis_init_stat['py_rtlsdr_get_xtal_freq'] = True

        self.__check_for_rtlsdr_devices()

        rtl_freq = c_uint32(0)
        tuner_freq = c_uint32(0)

        result  = self.clib.rtlsdr_get_xtal_freq(device_handle_ptr, 
                                                  byref(rtl_freq),
                                                  byref(tuner_freq))
        
        if result != 0:
            print_error_msg("Failed to fetch xtal freq. of tuner and RTL2832 chip.")
            raise ValueError
        return rtl_freq.value, tuner_freq.value
    
    def py_rtlsdr_set_center_freq(self, device_handle_ptr, center_freq):
        """
        Sets the center frequency of the tuner to the
        specified frequency.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
        * center_freq                           : (int) Center frequency to tune device to in Hz.
       
        Raises
        ------
        * ValueError
                                                * If fails to set the specified center freq.
                                                * If center freq is invalid.
        * TypeError
                                                * If type of center freq is not int.
        """

        if not self.__apis_init_stat['py_rtlsdr_set_center_freq']:
            f = self.clib.rtlsdr_set_center_freq
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev, c_uint32]
            self.__apis_init_stat['py_rtlsdr_set_center_freq'] = True

        self.__check_for_rtlsdr_devices()

        if int(center_freq) != center_freq:
            print_error_msg("Expected center freq to be int. Got: %s"%(type(center_freq)))
            raise TypeError
        
        center_freq = int(center_freq)

        if center_freq <= 0:
            print_error_msg("Expected center freq > 0. Got: %d"%(center_freq))
            raise ValueError

        result = self.clib.rtlsdr_set_center_freq(device_handle_ptr, c_uint32(center_freq))
        if result != 0:
            print_error_msg("Failed to set center freq to :%d"%(center_freq))
            raise ValueError


    def py_rtlsdr_get_center_freq(self,device_handle_ptr):
        """
        Reads and returns the center frequency of the tuner
        to which it is currently tuned to.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.

        Returns
        -------
        * center_freq                           : (int) Returns center frequency to which
                                                    device is tuned to in Hz.
       
        Raises
        ------
        * ValueError
                                                * If fails to read the center freq.
        
        """

        if not self.__apis_init_stat['py_rtlsdr_get_center_freq']:
            f = self.clib.rtlsdr_get_center_freq
            f.restype, f.argtypes = c_uint, [p_rtlsdr_dev]
            self.__apis_init_stat['py_rtlsdr_get_center_freq'] = True

        self.__check_for_rtlsdr_devices()
        
        center_freq = self.clib.rtlsdr_get_center_freq(device_handle_ptr)
        if center_freq == 0:
            print_error_msg("Failed to read the center freq of the tuner. Make sure to set the center freq before querying it.")
            raise ValueError
        return center_freq
    
    def py_rtlsdr_set_tuner_gain(self, device_handle_ptr, gain):
        """
        Set the specified gain value of the tuner.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
        * gain                                  : (float) gain to apply in db.
       
        Raises
        ------
        * ValueError
                                                * If fails to set the
                                                    gain value.
        * TypeError
                                                * If invalid/unsupported gain value
                                                    is specified.
        
        """

        if not self.__apis_init_stat['py_rtlsdr_set_tuner_gain']:
            f = self.clib.rtlsdr_set_tuner_gain
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev, c_int]
            self.__apis_init_stat['py_rtlsdr_set_tuner_gain'] = True

        self.__check_for_rtlsdr_devices()

        if float(gain) != gain:
            print_error_msg("Expected gain to be of type float. Got: %s", type(gain))
            raise TypeError
        
        supported_gain_values = self.py_rtlsdr_get_tuner_gains(device_handle_ptr)
        if gain not in supported_gain_values:
            print_error_msg("Invalid/Unsupported gain value %.1f dB is specified."%(gain))
            raise TypeError
        
        c_gain_value = int(gain * 10.0)
        result = self.clib.rtlsdr_set_tuner_gain(device_handle_ptr, c_int(c_gain_value))
        if result != 0:
            print_error_msg("Failed to set the specified gain value %.1f dB of the tuner."%(gain))
            raise ValueError

    
    def py_rtlsdr_get_tuner_gains(self, device_handle_ptr):
        """
        Returns the list of supported gain values of the tuner.
        The values are returned in dB.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
       
        Raises
        ------
        * ValueError
                                                * If fails to the read the supported
                                                    gain values.
        
        Returns
        -------
        * gain_values                           : (list) List of supported gain values
                                                    of the tuner in dB.
        """

        if not self.__apis_init_stat['py_rtlsdr_get_tuner_gains']:
            f = self.clib.rtlsdr_get_tuner_gains
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev, POINTER(c_int)]
            self.__apis_init_stat['py_rtlsdr_get_tuner_gains'] = True

        self.__check_for_rtlsdr_devices()

        c_gain_values_list = [-1] * 50
        c_gain_values_list = (c_int * len(c_gain_values_list))(*c_gain_values_list)
        
        result = self.clib.rtlsdr_get_tuner_gains(device_handle_ptr, c_gain_values_list)
        if result <= 0:
            print_error_msg("Failed to read supported gain values for the tuner.")
            raise ValueError
        
        gain_values = []
        for idx in range(0, result):
            gain_values.append(c_gain_values_list[idx]/10.0)
        return gain_values
    
    def py_rtlsdr_get_tuner_gain(self, device_handle_ptr):
        """
        Reads and Returns the current gain value of the tuner
        in dB.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
       
        Raises
        ------
        * ValueError
                                                * If fails to the read the
                                                    gain value of the tuner.
        
        Returns
        -------
        * gain_value                            : (float) Current gain value of the
                                                    tuner in dB.
        """

        if not self.__apis_init_stat['py_rtlsdr_get_tuner_gain']:
            f = self.clib.rtlsdr_get_tuner_gain
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev]
            self.__apis_init_stat['py_rtlsdr_get_tuner_gain'] = True

        self.__check_for_rtlsdr_devices()

        gain_value = self.clib.rtlsdr_get_tuner_gain(device_handle_ptr)
        if gain_value < 0:
            print_warn_msg("Failed to read current tuner gain value.")
            raise ValueError
        elif gain_value == 0:
            print_warn_msg("Returned gain value is 0 dB. The return value could be the error code or the gain value.")
        return gain_value/10.0

    def py_rtlsdr_set_freq_correction(self, device_handle_ptr, ppm):
        """
        Sets the frequency correction value. The value
        must in parts per million (ppm).

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
        * ppm                                   : (int) Frequency correction in ppm.
       
        Raises
        ------
        * ValueError
                                                * If fails to set the frequency correction.
        * TypeError   
                                                * If frequency correction value is invalid.
        """

        if not self.__apis_init_stat['py_rtlsdr_set_freq_correction']:
            f = self.clib.rtlsdr_set_freq_correction
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev, c_int]
            self.__apis_init_stat['py_rtlsdr_set_freq_correction'] = True

        self.__check_for_rtlsdr_devices()

        if int(ppm) != ppm:
            print_error_msg("Expected ppm to be of type int. Got: %s"%(type(ppm)))
            raise ValueError
        
        ppm = int(ppm)

        result = self.clib.rtlsdr_set_freq_correction(device_handle_ptr, c_int(ppm))
        if result != 0:
            print_error_msg("Failed to do the freq correction by %d"%(ppm))
            raise ValueError
    
    def py_rtlsdr_get_freq_correction(self, device_handle_ptr):
        """
        Reads and returns the frequency correction value. The value
        is returned in ppm.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
       
        Returns
        -------
         * ppm                                  : (int) Frequency correction in ppm.
        
        """

        if not self.__apis_init_stat['py_rtlsdr_get_freq_correction']:
            f = self.clib.rtlsdr_get_freq_correction
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev]
            self.__apis_init_stat['py_rtlsdr_get_freq_correction'] = True

        self.__check_for_rtlsdr_devices()

        freq_correction_value = self.clib.rtlsdr_get_freq_correction(device_handle_ptr)
        return freq_correction_value
    
    def py_rtlsdr_set_agc_mode(self, device_handle_ptr, enable=True):
        """
        Enable or disable the intenal AGC of the 
        RTL2832 chip.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
        * enable                                : (bool) Enable automatic gain contorl (agc). 
                                                    Default: True (enabled)
       
        Raises
        ------
        * ValueError
                                                * If fails to set the agc mode.
        * TypeError   
                                                * If enable is not of bool type.
        """
        if not self.__apis_init_stat['py_rtlsdr_set_agc_mode']:
            f = self.clib.rtlsdr_set_agc_mode
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev, c_int]
            self.__apis_init_stat['py_rtlsdr_set_agc_mode'] = True

        self.__check_for_rtlsdr_devices()

        if bool(enable) != enable:
            print_error_msg("Expected enable to be of bool type. Got: %s", type(enable))
            raise TypeError

        enable = bool(enable)

        if enable:
            enable_mode = 1
        else:
            enable_mode = 0
        
        result = self.clib.rtlsdr_set_agc_mode(device_handle_ptr, c_int(enable_mode))
        if result != 0:
            print_error_msg("Failed to set internal agc mode to %d."%(enable_manual_mode))
            raise ValueError

        if enable:
            print_info_msg("RTL2832 internal AGC is enabled.")
        else:
            print_info_msg("RTL2832 internal AGC is disabled.")
    
    def py_rtlsdr_set_sample_rate(self, device_handle_ptr, sample_rate):
        """
        Sets the sample rate of the device. 
        Valid sample rate range for R820 Tuner.
            226 ksps - 3.2 msps.
        Recomended to keep sample rate <= 2.8 msps.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
        * sample_rate                           : (int) Sample rate in Hz.
       
        Raises
        ------
        * ValueError
                                                * If fails to set the sample rate of the
                                                    device.
        * TypeError   
                                                * If sample rate type/value is invalid.
        """

        if not self.__apis_init_stat['py_rtlsdr_set_sample_rate']:
            f = self.clib.rtlsdr_set_sample_rate
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev, c_uint32]
            self.__apis_init_stat['py_rtlsdr_set_sample_rate'] = True

        self.__check_for_rtlsdr_devices()

        if int(sample_rate) != sample_rate:
            print_error_msg("Expected sample_rate to be of type int. Got: %s"%(type(sample_rate)))
            raise ValueError
        
        sample_rate = int(sample_rate)

        result = self.clib.rtlsdr_set_sample_rate(device_handle_ptr, c_uint32(sample_rate))
        if result != 0:
            print_error_msg("Failed to do the device sample rate to %d Hz."%(sample_rate))
            raise ValueError
    
    def py_rtlsdr_get_sample_rate(self, device_handle_ptr):
        """
        Get the current sample rate of the device in Hz.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
       
        Raises
        ------
        * ValueError
                                                * If fails to read the sample rate of
                                                    the device.
        
        Returns
        -------
        * sample_rate                           : (int) Returns the sample rate in Hz.
        """

        if not self.__apis_init_stat['py_rtlsdr_get_sample_rate']:
            f = self.clib.rtlsdr_get_sample_rate
            f.restype, f.argtypes = c_uint32, [p_rtlsdr_dev]
            self.__apis_init_stat['py_rtlsdr_get_sample_rate'] = True

        self.__check_for_rtlsdr_devices()
        
        sample_rate = self.clib.rtlsdr_get_sample_rate(device_handle_ptr)
        if sample_rate == 0:
            print_error_msg("Failed to read the device sample rate.")
            raise ValueError
        return sample_rate


    def py_rtlsdr_set_tuner_gain_mode(self, device_handle_ptr, manual=False):
        """
        Sets the tuner gain mode to automatic or
        manual.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.
        * manual                                : (bool) Enable manual tuner gain mode. 
                                                    Default: False (auto)
       
        Raises
        ------
        * ValueError
                                                * If fails to set the specified gain mode.
        * TypeError   
                                                * If manual is not of bool type.
        """

        if not self.__apis_init_stat['py_rtlsdr_set_tuner_gain_mode']:
            f = self.clib.rtlsdr_set_tuner_gain_mode
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev, c_int]
            self.__apis_init_stat['py_rtlsdr_set_tuner_gain_mode'] = True

        self.__check_for_rtlsdr_devices()

        if bool(manual) != manual:
            print_error_msg("Expected manual to be of bool type. Got: %s", type(manual))
            raise TypeError

        manual = bool(manual)

        if manual:
            enable_manual_mode = 1
        else:
            enable_manual_mode = 0
        
        result = self.clib.rtlsdr_set_tuner_gain_mode(device_handle_ptr, c_int(enable_manual_mode))
        if result != 0:
            print_error_msg("Failed to set tuner mode to %d."%(enable_manual_mode))
            raise ValueError

        if manual:
            print_info_msg("LNA/Tuner gain mode is set to manual.")
        else:
            print_info_msg("LNA/Tuner gain mode is set to automatic")
    
    def py_rtlsdr_reset_buffer(self, device_handle_ptr):
        """
        Resets the RTL2832 sample buffer.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.

        Raises
        ------
        * ValueError
                                                * If fails to reset the buffer.
        """
        if not self.__apis_init_stat['py_rtlsdr_reset_buffer']:
            f = self.clib.rtlsdr_reset_buffer
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev]
            self.__apis_init_stat['py_rtlsdr_reset_buffer'] = True

        self.__check_for_rtlsdr_devices()

        result = self.clib.rtlsdr_reset_buffer(device_handle_ptr)
        if result != 0:
            print_error_msg("Failed to reset the RTL2832 sample buffer.")
            raise ValueError
    
    '''
    def py_rtlsdr_is_tuner_PLL_locked(self, device_handle_ptr):
        """
        Reads and returns whether the tuner PLL 
        is locked to the center frequency. Tuner/PLL might 
        loose the lock at high frequencies due to temperature
        reasons.

        Parameters
        ----------
        * dev_handle_ptr                        : (p_rtlsdr_dev) Device handle pointer.

        Returns
        -------
        * pll_locked                            : (bool) Returns whether PLL is locked or
                                                    not.
       
        Raises
        ------
        * ValueError
                                                * If fails to read whether PLL islocked
                                                    or not.
        
        """

        if not self.__apis_init_stat['py_rtlsdr_is_tuner_PLL_locked']:
            f = self.clib.rtlsdr_is_tuner_PLL_locked
            f.restype, f.argtypes = c_int, [p_rtlsdr_dev]
            self.__apis_init_stat['py_rtlsdr_is_tuner_PLL_locked'] = True

        self.__check_for_rtlsdr_devices()
        
        pll_locked = self.clib.rtlsdr_is_tuner_PLL_locked(device_handle_ptr)
        print(pll_locked)
        
        if pll_locked == 0:
            return True
        elif pll_locked == 1:
            return False
        elif pll_locked == -2:
            print_error_msg("Checking PLL is locked on this tuner is not supported.")
            raise ValueError
        else:
            print_error_msg("Failed to check whether PLL is locked.")
            raise ValueError

    '''
