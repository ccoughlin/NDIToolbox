"""test_mainui_ctrl.py - tests the mainui_ctrl module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import mainmodel
from views import mainui
import wx
import unittest

class TestMainUIController(unittest.TestCase):
    """Tests the MainUIController class"""

    def setUp(self):
        self.app = wx.PySimpleApp()

    def test_init(self):
        """Verify proper initialization"""
        view = mainui.UI()
        ctrl = view.controller
        self.assertTrue(ctrl.view is view)
        self.assertTrue(isinstance(ctrl.model, mainmodel.MainModel))

    def test_get_bitmap(self):
        """Verify get_gitmap returns a wx.Bitmap or None if not found"""
        view = mainui.UI()
        ctrl = view.controller
        no_such_bitmap = "no icon.png"
        self.assertIsNone(ctrl.get_bitmap(no_such_bitmap))
        bitmap_exists = "tri_austin_logo.png"
        self.assertTrue(isinstance(ctrl.get_bitmap(bitmap_exists), wx.Bitmap))

if __name__ == "__main__":
    unittest.main()