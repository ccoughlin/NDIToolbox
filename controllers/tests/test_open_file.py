"""test_open_file.py - tests the open_file module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import open_file
import unittest

class TestOpenFile(unittest.TestCase):
    """Tests the open_file function"""

    def test_filenotfound(self):
        """Verify IOError raised if file not found"""
        with self.assertRaises(IOError):
            open_file.open_file('NO_SUCH_FILE')

if __name__ == "__main__":
    unittest.main()