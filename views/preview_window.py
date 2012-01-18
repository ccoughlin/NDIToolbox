"""preview_window.py - previews datasets for the Advanced NDE of Composites Project

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from controllers.preview_window_ctrl import PreviewWindowController
import ui_defaults
import dialogs
import wxspreadsheet
import wx
import numpy as np
import os.path

__author__ = 'Chris R. Coughlin'

class PreviewWindow(wx.Frame):
    """Basic wxPython wxFrame for previewing data in tabular format"""

    def __init__(self, parent, data_file, **read_text_params):
        self.parent = parent
        self.title = 'Preview - {0}'.format(os.path.basename(data_file))
        super(PreviewWindow, self).__init__(parent=self.parent, title=self.title)
        self.controller = PreviewWindowController(self, data_file, **read_text_params)
        self.init_ui()
        self.controller.load_data()

    def init_ui(self):
        """Creates and lays out the user interface"""
        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.spreadsheet = wxspreadsheet.Spreadsheet(self.main_panel)
        self.main_panel_sizer.Add(self.spreadsheet, 1, ui_defaults.sizer_flags, 0)
        self.main_panel.SetSizerAndFit(self.main_panel_sizer)