from pysdr.utils import *

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