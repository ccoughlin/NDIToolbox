"""preview_window_ctrl.py - controller for the PreviewWindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from models.preview_window_model import PreviewWindowModel
from models.mainmodel import get_logger
import wx

module_logger = get_logger(__name__)

__author__ = 'Chris R. Coughlin'

class PreviewWindowController(object):
    """Controller for the PreviewWindow"""

    def __init__(self, view, data_file):
        self.view = view
        self.model = PreviewWindowModel(self, data_file)
        module_logger.info("Successfully initialized PreviewWindowController.")

    @property
    def data(self):
        return self.model.data

    @data.setter
    def data(self, new_data):
        self.model.data = new_data

    def load_data(self, slice_idx=None):
        """Loads the data from the instance's data file, by default returning the entire data set (slice_idx is None).
        If slice_idx is a numpy.s_ slice operation, attempts to return a hyperslab (HDF5 feature - returns a slice
        of the data instead without loading the complete data)."""
        try:
            self.model.load_data(slice_idx)
        except MemoryError as err: # out of memory
            module_logger.exception("Insufficient memory - {0}".format(err))
            raise MemoryError("Insufficient memory to load data")

    def slice_data(self, slice_idx):
        """Sets the 3D data to a viewable 2D slice"""
        self.model.slice_data(slice_idx)

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
                module_logger.error("Unable to preview data, file too large to fit in memory.")
                err_msg = "The file is too large to load."
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Preview Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()

    def on_tb_click(self, evt):
        """Handles button click event from toolbar"""
        button = evt.GetId()
        if button == wx.ID_SAVE:
            self.export_text()
        elif button == 20: # Refresh data
            wx.BeginBusyCursor()
            self.populate_spreadsheet()
            wx.EndBusyCursor()

    def export_text(self):
        """Exports current spreadsheet to CSV file"""
        file_dlg = wx.FileDialog(parent=self.view, message="Please specify an output file",
                                 style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if file_dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()
            self.view.spreadsheet.WriteCSV(file_dlg.GetPath())
            wx.EndBusyCursor()
