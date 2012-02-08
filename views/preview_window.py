"""preview_window.py - previews datasets for the Advanced NDE of Composites Project

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from controllers.preview_window_ctrl import PreviewWindowController
import ui_defaults
import wxspreadsheet
import wx
import os.path
import threading

__author__ = 'Chris R. Coughlin'

class PreviewWindow(wx.Frame):
    """Basic wxPython wxFrame for previewing data in tabular format"""

    def __init__(self, parent, data_file, **read_text_params):
        self.parent = parent
        self.title = 'Preview - {0}'.format(os.path.basename(data_file))
        super(PreviewWindow, self).__init__(parent=self.parent, title=self.title)
        self.controller = PreviewWindowController(self, data_file, **read_text_params)
        self.init_ui()
        self.load_data()

    def load_data(self):
        data_thd = threading.Thread(target=self.controller.load_data)
        data_thd.setDaemon(True)
        data_thd.start()
        while True:
            data_thd.join(0.125)
            if not data_thd.is_alive():
                break
            wx.Yield()

    def init_ui(self):
        """Creates and lays out the user interface"""
        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.spreadsheet = wxspreadsheet.Spreadsheet(self.main_panel)
        self.main_panel_sizer.Add(self.spreadsheet, 1, ui_defaults.sizer_flags, 0)
        self.SetIcon(self.parent.GetIcon())
        self.main_panel.SetSizerAndFit(self.main_panel_sizer)