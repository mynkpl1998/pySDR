from pysdr.rtlsdr import librtlsdr

if __name__ == "__main__":

    obj = librtlsdr()
    
    device_name = obj.py_rtlsdr_get_device_name(device_index=0)
    print(device_name)
    out = obj.py_rtlsdr_get_device_usb_strings(device_index=0)
    print(out)