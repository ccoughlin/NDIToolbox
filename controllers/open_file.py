"""open_file.py - opens a file with the associated application (Windows, OS X, POSIX)

Chris R. Coughlin (TRI/Austin, Inc.)

Based on discussion and code from StackOverflow:
http://stackoverflow.com/questions/434597/open-document-with-default-application-in-python

License:  BSD
"""

__author__ = 'Chris R. Coughlin'

from models.mainmodel import get_logger
import subprocess
import os
import warnings

module_logger = get_logger(__name__)

def open_file(filename):
    """Opens the file filename with its associated application.
    Windows, POSIX, OS X supported directly; other OSes may
    also work but function will issue a warning.

    Exceptions:
    IOError - file not found
    WindowsError - no associated application for this filetype, application not found (Windows only)
    OSError - application not found
    """
    if not os.path.exists(filename):
        module_logger.error("File '{0}' not found.".format(filename))
        raise IOError("File not found")
    if os.name == 'nt':
        os.startfile(filename)
    else:
        if os.name == 'mac':
            cmd = 'open'
        elif os.name == 'posix':
            cmd = 'xdg-open'
        else:
            warnings.warn('Possibly unsupported OS')
            module_logger.warning('Possibly unsupported operating system')
            cmd = 'open'
        try:
            subprocess.check_call((cmd, filename))
        except subprocess.CalledProcessError:  # Open return code wasn't zero, redirect to an OSError
            module_logger.error("Subprocess call returned non-zero, unidentified error occurred.")
            raise OSError("Unable to open file with associated application")