'''test_ui_defaults.py - tests the ui_defaults module

Chris R. Coughlin (TRI/Austin, Inc.)
'''

__author__ = 'Chris R. Coughlin'

import wx
import unittest
from views import ui_defaults

class TestUIDefaults(unittest.TestCase):
    '''Tests the ui_defaults module'''

    def test_widget_margin(self):
        '''Verify a default margin around widgets has been set'''
        self.assertEqual(3, ui_defaults.widget_margin)

    def test_label_pct(self):
        '''Verify a resizing factor for labels has been set'''
        self.assertEqual(0.25, ui_defaults.lbl_pct)

    def test_ctrl_pct(self):
        '''Verify a resizing factor for controls has been set'''
        self.assertEqual(1.0, ui_defaults.ctrl_pct)

    def test_sizer_flags(self):
        '''Verify defaults for re-sizing wxPython controls'''
        self.assertEqual(wx.ALL|wx.EXPAND, ui_defaults.sizer_flags)

    def test_lblsizer_flags(self):
        '''Verify defaults for re-sizing wxPython labels'''
        self.assertEqual(wx.ALIGN_CENTER_VERTICAL|wx.ALL, ui_defaults.lblsizer_flags)

if __name__ == "__main__":
    unittest.main()