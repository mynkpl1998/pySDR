from pysdr.rtlsdr import librtlsdr

if __name__ == "__main__":

    obj = librtlsdr()
    '''  
    device_name = obj.py_rtlsdr_get_device_name(device_index=0)
    print(device_name)
    out = obj.py_rtlsdr_get_device_usb_strings(device_index=0)
    print(out)
    out = obj.py_rtlsdr_get_index_by_serial(serial_id='00000001')
    print(out)
    '''
    dev_p = obj.py_rtlsdr_open(device_index=0)
    #print(dev_p)
    rtl_freq, tuner_freq = obj.py_rtlsdr_get_xtal_freq(dev_p)
    print("XO Freq: ", rtl_freq, tuner_freq)
    
    center_freq = 433e6
    obj.py_rtlsdr_set_center_freq(dev_p, center_freq)
    print("Center freq: ", obj.py_rtlsdr_get_center_freq(dev_p))

    obj.py_rtlsdr_set_tuner_gain_mode(dev_p, manual=True)

    gain_values = obj.py_rtlsdr_get_tuner_gains(dev_p)
    print("Supported gain values: ", gain_values)

    set_gain_value = 0.9
    obj.py_rtlsdr_set_tuner_gain(dev_p, set_gain_value)

    current_lna_gain = obj.py_rtlsdr_get_tuner_gain(dev_p)
    print("LNA Gain value: ", current_lna_gain, " dB")
    
    freq_corr_returned = obj.py_rtlsdr_get_freq_correction(dev_p)
    print("Before setting freq correction: ", freq_corr_returned)

    ppm = -200
    obj.py_rtlsdr_set_freq_correction(dev_p, ppm)
    
    freq_corr_returned = obj.py_rtlsdr_get_freq_correction(dev_p)
    print("After setting freq correction: ", freq_corr_returned)
    
    obj.py_rtlsdr_set_agc_mode(dev_p, enable=False)

    sample_rate = 2.3e6
    obj.py_rtlsdr_set_sample_rate(dev_p, sample_rate)

    returned_sample_rate = obj.py_rtlsdr_get_sample_rate(dev_p)
    print("After setting sample rate: ", returned_sample_rate)

    obj.py_rtlsdr_reset_buffer(dev_p)

    obj.py_rtlsdr_close(dev_p)