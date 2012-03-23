"""preview_window_ctrl.py - controller for the PreviewWindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from models.preview_window_model import PreviewWindowModel
import wx

__author__ = 'Chris R. Coughlin'

class PreviewWindowController(object):
    """Controller for the PreviewWindow"""

    def __init__(self, view, data_file, **read_text_params):
        self.view = view
        self.model = PreviewWindowModel(self, data_file, **read_text_params)

    def load_data(self):
        """Loads the instance's data file"""
        self.model.load_data()

    def populate_spreadsheet(self):
        """Fills the PreviewWindow's spreadsheet with the
        current data set."""
        if self.model.data is not None:
            try:
                self.view.spreadsheet.ClearGrid()
                self.view.spreadsheet.SetNumberRows(0)
                self.view.spreadsheet.SetNumberCols(0)
                rownum = 0
                if self.model.data.ndim == 2:
                    num_rows = self.model.data.shape[0]
                    for row in range(num_rows):
                        self.view.spreadsheet.AppendRows(1)
                        numcols = self.model.data[row].size
                        if self.view.spreadsheet.GetNumberCols() < numcols:
                            self.view.spreadsheet.SetNumberCols(numcols)
                        colnum = 0
                        for cell in self.model.data[row]:
                            self.view.spreadsheet.SetCellValue(rownum, colnum, str(cell))
                            colnum += 1
                        rownum += 1
                elif self.model.data.ndim == 1:
                    self.view.spreadsheet.SetNumberCols(1)
                    for el in self.model.data:
                        self.view.spreadsheet.AppendRows(1)
                        self.view.spreadsheet.SetCellValue(rownum, 0, str(el))
                        rownum += 1
            except MemoryError: # File too large to load
                err_msg = "The file is too large to load."
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Preview Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()