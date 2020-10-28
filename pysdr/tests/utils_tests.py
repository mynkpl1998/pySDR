from pysdr.utils import *
from ctypes import c_ubyte, POINTER, byref

def test_print_error_msg():
    """
    Verifies the print_error_msg function.
    The function should print the passed 
    message to the function to console in
    read color.
    Please pass -s argument to validate
    the printing while running tests.
    """
    message = "This is a test error message. This should be printed in red."
    print_error_msg(message)

def test_print_info_msg():
    """
    Verifies the print_info_msg function.
    The function should print the passed 
    message to the function to console in
    blue color.
    Please pass -s argument to validate
    the printing while running tests.
    """
    message = "This is a test information message. This should be printed in blue."
    print_info_msg(message)

def test_print_success_msg():
    """
    Verifies the print_success_msg function.
    The function should print the passed 
    message to the function to console in
    green color.
    Please pass -s argument to validate
    the printing while running tests.
    """
    message = "This is a test success message. This should be printed in green."
    print_success_msg(message)

def test_print_warn_msg():
    """
    Verifies the print_warn_msg function.
    The function should print the passed 
    message to the function to console in
    yellow color.
    Please pass -s argument to validate
    the printing while running tests.
    """
    message = "This is a test warning message. This should be printed in yellow."
    print_warn_msg(message)

def test_c_ubyte_ptr_to_string_size_based():
    """
    Verifies the c_ubyte_ptr_to_string.
    The function should return the string
    by reading byte at a time till the 
    specified size.
    """
    sample_string = (c_ubyte * 6)()
    sample_string[0] = 65
    sample_string[1] = 66
    sample_string[2] = 67
    sample_string[3] = 68
    sample_string[4] = 69
    sample_string[5] = 70

    assert c_ubyte_ptr_to_string(sample_string, 6) == "ABCDEF"

def test_c_ubyte_ptr_to_string_null_based():
    """
    Verifies the c_ubyte_ptr_to_string.
    The function should return the string
    by reading byte at a time till the 
    0x00 is encountered.
    """
    sample_string = (c_ubyte * 6)()
    sample_string[0] = 65
    sample_string[1] = 66
    sample_string[2] = 0x00
    sample_string[3] = 68
    sample_string[4] = 69
    sample_string[5] = 70

    assert c_ubyte_ptr_to_string(sample_string, 6) == "AB"

def test_cstr():
    """
    Verifies the cstr function.
    The function should return the cstring.
    """
    sample_string = "abcdef"
    csample_string = cstr(sample_string)
    assert sample_string == csample_string