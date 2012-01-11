'''test_mainui_ctrl.py - tests the mainui_ctrl module

Chris R. Coughlin (TRI/Austin, Inc.)
'''

__author__ = 'Chris R. Coughlin'

from models import mainmodel
from views import mainui
import wx
import unittest

class TestMainUIController(unittest.TestCase):
    '''Tests the MainUIController class'''

    def setUp(self):
        self.app = wx.PySimpleApp()

    def test_init(self):
        '''Verify proper initialization'''
        view = mainui.UI()
        ctrl = view.controller
        self.assertTrue(ctrl.view is view)
        self.assertTrue(isinstance(ctrl.model, mainmodel.MainModel))

if __name__ == "__main__":
    unittest.main()