from colorama import init
from colorama import Fore, Style

# Intializes the colorama library.
init()

def print_error_msg(msg):
    """
    The function can be used to print
    error messages to the console. The
    message is printed in red color.

    Parameters
    ----------
        msg: The message to print on the console.
    """
    print(Style.BRIGHT + Fore.RED + "[x]: ", msg, Style.RESET_ALL)

def print_info_msg(msg):
    """
    The function can be used to print
    information to the console. The
    message is printed in blue color.

    Parameters
    ----------
        msg: The message to print on the console.
    """
    print(Style.BRIGHT + Fore.BLUE + "[i]: ", msg, Style.RESET_ALL)

def print_success_msg(msg):
    """
    The function can be used to print
    success messages to the console. The
    message is printed in green color.

    Parameters
    ----------
        msg: The message to print on the console.
    """
    print(Style.BRIGHT + Fore.GREEN + "[*]: ", msg, Style.RESET_ALL)

def print_warn_msg(msg):
    """
    The function can be used to print
    warning messages to the console. The
    message is printed in yellow color.

    Parameters
    ----------
        msg: The message to print on the console.
    """
    print(Style.BRIGHT + Fore.YELLOW + "[~]: ", msg, Style.RESET_ALL)

def c_ubyte_ptr_to_string(c_ubyte_pointer, size):
    """
    Returns the string pointed by the c_ubyte
    pointer.
    
    Parameters
    ----------
    * c_ubyte_pointer                 : Pointer to starting of the buffer.
    * size                            : Size of the buffer to read.
    """
    buffer_str = ''
    for idx in range(0, size):
        if chr(c_ubyte_pointer[idx]) == '\x00':
            break
        buffer_str += chr(c_ubyte_pointer[idx])
    return buffer_str