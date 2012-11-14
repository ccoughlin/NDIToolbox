"""preview_window.py - previews datasets for the Advanced NDE of Composites Project

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from controllers.preview_window_ctrl import PreviewWindowController
from controllers import pathfinder
from models import workerthread
from models.mainmodel import get_logger
from views import dialogs
import ui_defaults
import wxspreadsheet
import wx
import os.path
import Queue

__author__ = 'Chris R. Coughlin'

module_logger = get_logger(__name__)

class PreviewWindow(wx.Frame):
    """Basic wxPython wxFrame for previewing data in tabular format"""

    def __init__(self, parent, data_file):
        self.parent = parent
        self.title = 'Preview - {0}'.format(os.path.basename(data_file))
        super(PreviewWindow, self).__init__(parent=self.parent, title=self.title)
        self.controller = PreviewWindowController(self, data_file)
        self.init_ui()
        module_logger.info("Successfully initialized PreviewWindow.")
        self.load_data()

    def has_data(self):
        """Returns True if data is not None"""
        return self.controller.data is not None

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
                    module_logger.error("Unable to load data: {0}".format(exc))
                    err_msg = "An error occurred while loading data:\n{0}".format(exc)
                    if len(err_msg) > 150:
                        # Truncate lengthy error messages
                        err_msg = ''.join([err_msg[:150], "\n(continued)"])
                    err_dlg = wx.MessageDialog(self.parent, message=err_msg,
                                               caption="Unable To Load Data", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                except Queue.Empty:
                    pass
                break
            wx.GetApp().Yield(True)
        if self.has_data():
            if self.controller.data.ndim == 3:
                module_logger.info("Data are 3D, requesting planar slice.")
                slice_dlg = dialogs.PlanarSliceDialog(parent=self, data_shape=self.controller.data.shape,
                                                      title="Specify 2D Plane")
                if slice_dlg.ShowModal() == wx.ID_OK:
                    self.controller.load_data(slice_dlg.get_data_slice())
                module_logger.info("User cancelled planar slice operation.")
                slice_dlg.Destroy()
            self.controller.populate_spreadsheet()

    def init_ui(self):
        """Creates and lays out the user interface"""
        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.spreadsheet = wxspreadsheet.Spreadsheet(self.main_panel)
        self.init_toolbar()
        self.main_panel_sizer.Add(self.spreadsheet, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)
        self.SetIcon(self.parent.GetIcon())
        self.main_panel.SetSizerAndFit(self.main_panel_sizer)

    def init_toolbar(self):
        """Creates a simple toolbar for the spreadsheet window"""
        self.spreadsheet_tb = wx.ToolBar(self.main_panel,
                                         style=wx.TB_VERTICAL | wx.TB_FLAT | wx.TB_NODIVIDER | wx.NO_BORDER)
        self.spreadsheet_tb.SetToolBitmapSize((16, 16))
        self.spreadsheet_tb.AddSimpleTool(20, self.get_bitmap("Refresh.png"), "Reload Data")
        self.spreadsheet_tb.AddSimpleTool(wx.ID_SAVE, self.get_bitmap("Save.png"),
                                          "Export As CSV Text File")
        self.Bind(wx.EVT_TOOL, self.controller.on_tb_click, id=20)
        self.Bind(wx.EVT_TOOL, self.controller.on_tb_click, id=wx.ID_SAVE)
        self.spreadsheet_tb.Realize()
        self.main_panel_sizer.Add(self.spreadsheet_tb, 0, wx.TOP, border=0)

    def get_bitmap(self, bitmap_name):
        """Given the base name for a file, returns a wx Bitmap instance from the bitmap folder"""
        return wx.Bitmap(os.path.join(pathfinder.bitmap_path(), bitmap_name))