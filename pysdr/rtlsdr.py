import numpy as np
from ctypes import c_void_p
from pysdr.rtlsdr_apis import librtlsdr
from pysdr.utils import print_error_msg, print_info_msg, print_success_msg, print_warn_msg

class Radio:
    """
    Creates an object to interact with the RTL-SDR
    device for the specified device index.
    The number of RTL-SDR devices connected to the
    host can be returned by querying py_rtlsdr_get_device_count 
    api.

    Parameters
    ----------
    * device_index                          : (int) RTL-SDR device index.
    * logging_level                         : (int) 1 - Enable all (success, info and warning messages.)
                                                    2 - Enable warning and info messages only, 
                                                    3 - Enable warnings only.
                                                    4 - Disable all messages.
                                                    Default: 3.
    Raises
    ------
    * TypeError
                                            * If device index specified is invalid.

    Attributes
    ----------
    * clib                                  * (librtlsdr) Device librtlsdr object.
    * center_freq                           * (int) Center freq of the device in Hz.
    * sample_rate                           * (int) Sample Rate of the device in Hz.
    * freq_correction                       * (int) Frequency correction in ppm.
    * enable_agc                            * (bool) Whether AGC is enabled.
    * tuner_gain                            * (float) Current tuner gain in dB.
    * tuner_gains                           * (list) List of supported gain values for tuner in dB.
    * enable_auto_tuner_gain                * (bool) Gain selection mode of the tuner. Auto - True, manual - False.
    * tuner_xo_freq                         * (int) Tuner crystal frequency in Hz.
    * rtl_xo_freq                           * (int) RTL2832 crystal frequency in Hz.
    * num_recv_samples                      * (np.array) Number of samples to read from the SDR. 

    """

    def __init__(self, device_index, logging_level=3):
        self.__librtlsdr = librtlsdr()

        if int(device_index) != device_index:
            print_error_msg("Expected device index to be of int. Got: %s."%(type(device_index)))
            raise TypeError
        
        device_index = int(device_index)

        self.__device_index = device_index

        if int(logging_level) != logging_level:
            print_error_msg("Expected logging level to be int. Got: %s"%(type(logging_level)))
            raise TypeError

        logging_level = int(logging_level)

        if logging_level < 1 or logging_level > 4:
            print_error_msg("Invalid logging level %d."%(logging_level))
            raise ValueError
        
        # Setting the logging level.
        self.__logging_level = logging_level

        # Open a device pointer to the SDR.
        self.__dev_ptr = c_void_p(None)
        self.__dev_ptr = self.clib.py_rtlsdr_open(device_index)
        
        if self.__logging_level == 1:
            print_success_msg("Successfully opened a libusb connection to the device.")

        # Get SDR details
        self.__mid, self.__vid, self.__serial = self.clib.py_rtlsdr_get_device_usb_strings(self.__device_index)
        if self.__logging_level < 3:
            device_strings = "Manufacturer: %s, Vendor ID: %s, Serial %s."%(self.__mid, self.__vid, self.__serial)
            print_info_msg(device_strings)
        
        # Attributes
        self.__center_freq = None
        self.__sample_rate = None
        self.__enable_agc = None
        self.__tuner_gain = None
        self.__enable_auto_tuner_gain = None
        self.__tuner_gains = self.clib.py_rtlsdr_get_tuner_gains(self.__dev_ptr)
        self.__freq_correction = self.clib.py_rtlsdr_get_freq_correction(self.__dev_ptr)
        self.__rtl_xo_freq, self.__tuner_xo_freq = self.clib.py_rtlsdr_get_xtal_freq(self.__dev_ptr)
        self.__num_recv_samples = None

        # Init defaults
        self.__init_default()

        # Reset libusb buffer
        self.clib.py_rtlsdr_reset_buffer(self.__dev_ptr)

        if self.__logging_level < 3:
            device_config = 'Intialized device with following default values.'
            device_config += '\n\t1. Center Freq: %d Hz.'%(self.center_freq)
            device_config += '\n\t2. Sample Rate: %d MSPS.'%(self.sample_rate)
            device_config += '\n\t3. AGC Enabled: %s.'%(self.enable_agc)
            device_config += '\n\t4. Automatic tuner gain selection: %s.'%(self.enable_auto_tuner_gain)
            device_config += '\n\t5. Freq Correction: %d ppm'%(self.freq_correction)
            device_config += '\n\t6. Tuner gain: %s dB'%(self.tuner_gain)
            device_config += '\n\t7. Frame size (samples/frame): %d'%(self.num_recv_samples)
            print_info_msg(device_config)
    
    @property
    def tuner_gain(self):
        self.__tuner_gain = self.clib.py_rtlsdr_get_tuner_gain(self.__dev_ptr)
        return self.__tuner_gain
    
    @property
    def num_recv_samples(self):
        return self.__num_recv_samples
    
    @property
    def dev_ptr(self):
        return self.__dev_ptr

    @property
    def freq_correction(self):
        self.__freq_correction = self.clib.py_rtlsdr_get_freq_correction(self.__dev_ptr)
        return self.__freq_correction
    
    @property
    def enable_auto_tuner_gain(self):
        return self.__enable_auto_tuner_gain
    
    @property
    def clib(self):
        return self.__librtlsdr
    
    @property
    def tuner_gains(self):
        return self.__tuner_gains
    
    @property
    def center_freq(self):
        self.__center_freq = self.clib.py_rtlsdr_get_center_freq(self.__dev_ptr)
        return self.__center_freq
    
    @property
    def sample_rate(self):
        self.__sample_rate = self.clib.py_rtlsdr_get_sample_rate(self.__dev_ptr)
        return self.__sample_rate
    
    @property
    def enable_agc(self):
        return self.__enable_agc
    
    @property
    def tuner_xo_freq(self):
        _, self.__tuner_xo_freq = self.clib.py_rtlsdr_get_xtal_freq(self.__dev_ptr)
        return self.__tuner_xo_freq
    
    @property
    def rtl_xo_freq(self):
        self.__rtl_xo_freq, _ = self.clib.py_rtlsdr_get_xtal_freq(self.__dev_ptr)
        return self.__rtl_xo_freq
    
    @freq_correction.setter
    def freq_correction(self, ppm):
        self.clib.py_rtlsdr_set_freq_correction(self.__dev_ptr, ppm)
        self.__freq_correction = ppm
        
        returned_freq_correction = self.clib.py_rtlsdr_get_freq_correction(self.__dev_ptr)
        if self.__logging_level == 1:
            print_success_msg("Freq correct is set to %d ppm"%(ppm))
    
    @center_freq.setter
    def center_freq(self, freq):
        self.clib.py_rtlsdr_set_center_freq(self.__dev_ptr, freq)
        self.__center_freq = freq
        
        returned_center_freq = self.clib.py_rtlsdr_get_center_freq(self.__dev_ptr)
        if self.__logging_level == 1:
            print_success_msg("Device center freq is set to %d Hz."%(returned_center_freq))

    
    @sample_rate.setter
    def sample_rate(self, rate):
        self.clib.py_rtlsdr_set_sample_rate(self.__dev_ptr, rate)
        self.__sample_rate = rate

        returned_sample_rate = self.clib.py_rtlsdr_get_sample_rate(self.__dev_ptr)
        if self.__logging_level == 1:
            print_success_msg("Device sample rate is set to %d Hz."%(returned_sample_rate))

    @enable_agc.setter
    def enable_agc(self, enable):
        self.clib.py_rtlsdr_set_agc_mode(self.__dev_ptr, enable=enable)
        self.__enable_agc = enable
        if self.__logging_level == 1:
            if enable:
                print_success_msg("Device internal AGC is enabled.")
            else:
                print_success_msg("Device internal AGC is disabled.")
    
    @tuner_gain.setter
    def tuner_gain(self, gain):
        """
        Make sure tuner gain selection mode is set to manual
        before over writing the value.
        """
        self.__enable_auto_tuner_gain = False
        self.clib.py_rtlsdr_set_tuner_gain(self.__dev_ptr, gain)
        self.__tuner_gain = gain
        if self.__logging_level == 1:
            print_success_msg("Tuner gain is set to %d dB"%(gain))
        
    @num_recv_samples.setter
    def num_recv_samples(self, num_samples):
        if type(num_samples) != int:
            print_error_msg("Expected int. Got: %s"%(type(num_samples)))
            raise ValueError
        
        self.__num_recv_samples = num_samples
    
    @enable_auto_tuner_gain.setter
    def enable_auto_tuner_gain(self, enable):
        if type(enable) != bool:
            print_error_msg("Expected bool. Got: %s"%(type(enable)))
            raise ValueError
    
        self.clib.py_rtlsdr_set_tuner_gain_mode(self.__dev_ptr, manual=not enable)
        self.__enable_auto_tuner_gain = enable
        if self.__logging_level == 1:
            if enable:
                print_success_msg("Tuner gain selection is set to auto.")
            else:
                print_success_msg("Tuner gain selection is set to manual.")

    def __init_default(self):
        """
        Intializes the default values of the SDR.
        """
        if self.__logging_level < 3:
            print_info_msg("Intializing device with default values.")
        
        center_freq = 980e6     # 980 Mhz
        sample_rate = 2e6       # 2 MSPS
        agc = True              # Enable AGC 
        auto_lna_gain = True    # Enable automatic lna gain selection
        auto_tuner_gain_mode = True # Set tuner gain mode to auto.
        num_samples = 512       # Number of samples to read from SDR

        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.enable_agc = agc
        self.enable_auto_tuner_gain = auto_tuner_gain_mode
        self.num_recv_samples = num_samples
    
    def print_device_configuration(self,):
        """
        Prints the correct device configuration to
        the console.
        """
        device_config = 'Current device settings.'
        device_config += '\n\t1. Center Freq: %d Hz.'%(self.center_freq)
        device_config += '\n\t2. Sample Rate: %d MSPS.'%(self.sample_rate)
        device_config += '\n\t3. AGC Enabled: %s.'%(self.enable_agc)
        device_config += '\n\t4. Automatic tuner gain selection: %s.'%(self.enable_auto_tuner_gain)
        device_config += '\n\t5. Freq Correction: %d ppm'%(self.freq_correction)
        device_config += '\n\t6. Tuner gain: %s dB'%(self.tuner_gain)
        device_config += '\n\t7. Frame size (samples/frame): %d'%(self.num_recv_samples)
        print_info_msg(device_config)


    def __repr__(self,):
        object_str = str({'Device Index': self.__device_index, 
                           'Logging Level': self.__logging_level,
                           'Manufacturer': self.__mid,
                           'Vendor ID': self.__vid, 
                           'Serial': self.__serial,
                           'Supported tuner gain values in dB': self.tuner_gains,
                           'Freq correction (ppm)': self.freq_correction,
                           'Center freq (Hz)': self.center_freq,
                           'Sample rate (MSPS)': self.sample_rate,
                           'AGC': 'enabled' if self.enable_agc else 'disabled',
                           'Tuner gain selection': 'auto' if self.enable_auto_tuner_gain else 'manual',
                           'Tuner gain (dB)': self.tuner_gain,
                           'Tuner xtal freq (Hz)': self.tuner_xo_freq,
                           'RTL2832 xtal freq (Hz)': self.rtl_xo_freq,
                           'Frame Size (samples/frame)': self.num_recv_samples
                           })
        return object_str
    
    def rx_samples(self):
        """
        Reads and returns the specifed number 
        of IQ samples from the device.

        Returns
        -------
        * samples                       :  (np.array) A numpy array of samples of 
                                            complex type is returned. (Normalized)
        """
        frame_latency, raw_data = self.clib.py_rtlsdr_read_sync(self.__dev_ptr, self.num_recv_samples)
        iq = raw_data.astype(np.float64).view(np.complex128)
        iq /= 127.5
        iq -= (1 + 1j)
        
        empirical_sample_rate = (self.num_recv_samples/frame_latency) * 1000
        if empirical_sample_rate < self.sample_rate:
            if self.__logging_level < 4:
                print_warn_msg("Empirical sample rate: %.4f MSPS. Requested sample rate: %d MSPS."%(empirical_sample_rate, self.sample_rate))

        if self.__logging_level < 3:
            print_info_msg("Empirical sample rate: %.4f MSPS. Requested sample rate: %d MSPS."%(empirical_sample_rate, self.sample_rate))
            
        return iq
    
    def close(self, ):
        """
        Closes the libusb connection to the SDR device.
        """
        if self.__dev_ptr.value is not None:
            self.clib.py_rtlsdr_close(self.__dev_ptr)
            if self.__logging_level == 1:
                print_success_msg("Successfully closed the libusb connection to the device.")
        else:
            if self.__logging_level < 4:
                print_warn_msg("Device handle pointer is None. Skipping close libusb connection to the device.")
        self.__dev_ptr = c_void_p(None)

    def __del__(self):
        """
        Device clearn up function. This function
        is called when the object goes out of scope.
        Closes the connection to the device.
        """

        if self.__dev_ptr.value is not None:
            self.clib.py_rtlsdr_close(self.__dev_ptr)
            if self.__logging_level == 1:
                print_success_msg("Successfully closed the libusb connection to the device.")
        else:
            if self.__logging_level < 4:
                print_warn_msg("Device handle pointer is None. Skipping close libusb connection to the device.")
        self.__dev_ptr = c_void_p(None)