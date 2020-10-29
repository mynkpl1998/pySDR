from pysdr.rtlsdr import Radio
from pysdr.rtlsdr_apis import librtlsdr

if __name__ == "__main__":

    rtlsdr_lib = librtlsdr()
    num_devices = rtlsdr_lib.py_rtlsdr_get_device_count()
    print("Number of attached devices: ", num_devices)
    sdr = Radio(device_index=0, logging_level=1)
    #print(sdr)