"""preview_window.py - previews datasets for the Advanced NDE of Composites Project

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from controllers.preview_window_ctrl import PreviewWindowController
from models import workerthread
import ui_defaults
import wxspreadsheet
import wx
import os.path
import Queue

__author__ = 'Chris R. Coughlin'

class PreviewWindow(wx.Frame):
    """Basic wxPython wxFrame for previewing data in tabular format"""

    def __init__(self, parent, data_file):
        self.parent = parent
        self.title = 'Preview - {0}'.format(os.path.basename(data_file))
        super(PreviewWindow, self).__init__(parent=self.parent, title=self.title)
        self.controller = PreviewWindowController(self, data_file)
        self.init_ui()
        self.load_data()

    def load_data(self):
        exception_queue = Queue.Queue()
        data_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                             target=self.controller.load_data)
        data_thd.start()
        while True:
            data_thd.join(0.125)
            if not data_thd.is_alive():
                try:
                    exc_type, exc = exception_queue.get(block=False)
                    err_msg = "An error occurred while loading data:\n{0}".format(exc)
                    if len(err_msg) > 150:
                        # Truncate NumPy's genfromtxt() method's lengthy error messages
                        err_msg = ''.join([err_msg[:150], "\n(continued)"])
                    err_dlg = wx.MessageDialog(self.parent, message=err_msg,
                                               caption="Unable To Load Data", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                except Queue.Empty:
                    pass
                break
            wx.GetApp().Yield(True)
        if self.controller.data.ndim == 3:
            min_slice_idx = 0
            max_slice_idx = self.controller.data.shape[2]-1
            msg = "Please specify a slice index to plot from the 3D array."
            rng_caption = "Slice From Array ({0}-{1}):".format(min_slice_idx, max_slice_idx)
            slice_dlg = wx.NumberEntryDialog(self, message=msg, prompt=rng_caption,
                                             caption="Specify 2D Slice", value=0, min=min_slice_idx,
                                             max=max_slice_idx)
            if slice_dlg.ShowModal() == wx.ID_OK:
                self.controller.slice_data(slice_dlg.GetValue())
            slice_dlg.Destroy()
        self.controller.populate_spreadsheet()

    def init_ui(self):
        """Creates and lays out the user interface"""
        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.spreadsheet = wxspreadsheet.Spreadsheet(self.main_panel)
        self.main_panel_sizer.Add(self.spreadsheet, 1, ui_defaults.sizer_flags, 0)
        self.SetIcon(self.parent.GetIcon())
        self.main_panel.SetSizerAndFit(self.main_panel_sizer)