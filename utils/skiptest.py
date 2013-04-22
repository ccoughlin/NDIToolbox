"""skiptest.py - provides a decorator to skip a unit test if a given module is not found.

Chris R. Coughlin (TRI/Austin, Inc.)
"""

import imp
import unittest

def skipIfModuleNotInstalled(*modules):
    """Skipping test decorator - skips test if import of module
    fails."""
    try:
        for module in modules:
            imp.find_module(module)
        return lambda func: func
    except ImportError:
        return unittest.skip("Test skipped; required module(s) {0} not installed.".format(','.join(modules)))