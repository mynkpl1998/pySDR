from pysdr.rtlsdr import Radio
from pysdr.rtlsdr_apis import librtlsdr

if __name__ == "__main__":

    rtlsdr_lib = librtlsdr()
    num_devices = rtlsdr_lib.py_rtlsdr_get_device_count()
    print("Number of attached devices: ", num_devices)
    sdr = Radio(device_index=0, logging_level=1)
    
    print(sdr)
    sdr.center_freq = 433e6
    sdr.enable_auto_tuner_gain = True
    samples = sdr.rx_samples()
    #print(samples)
    # Create an example to demonstrate the usage in github readme