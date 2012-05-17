"""open_file.py - opens a file with the associated application (Windows, OS X, POSIX)

Chris R. Coughlin (TRI/Austin, Inc.)

Based on discussion and code from StackOverflow:
http://stackoverflow.com/questions/434597/open-document-with-default-application-in-python

License:  BSD
"""

__author__ = 'Chris R. Coughlin'

import subprocess
import os
import os.path
import warnings

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
            cmd = 'open'
        try:
            subprocess.check_call((cmd, filename))
        except subprocess.CalledProcessError:  # Open return code wasn't zero, redirect to an OSError
            raise OSError("Unable to open file with associated application")