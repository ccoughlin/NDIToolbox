"""preview_window_ctrl.py - controller for the PreviewWindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from models.preview_window_model import PreviewWindowModel

__author__ = 'Chris R. Coughlin'

class PreviewWindowController(object):
    """Controller for the PreviewWindow"""

    def __init__(self, view, data_file, **read_text_params):
        self.view = view
        self.model = PreviewWindowModel(self, data_file, **read_text_params)

    def load_data(self):
        """Loads the instance's data file and updates the PreviewWindow's
        spreadsheet with the contents"""
        data = self.model.load_data()
        if data is not None:
            self.view.spreadsheet.ClearGrid()
            self.view.spreadsheet.SetNumberRows(0)
            self.view.spreadsheet.SetNumberCols(0)
            rownum = 0
            if data.ndim==2:
                num_rows = data.shape[0]
                for row in range(num_rows):
                    self.view.spreadsheet.AppendRows(1)
                    numcols = data[row].size
                    if self.view.spreadsheet.GetNumberCols() < numcols:
                        self.view.spreadsheet.SetNumberCols(numcols)
                    colnum = 0
                    for cell in data[row]:
                        self.view.spreadsheet.SetCellValue(rownum, colnum, str(cell))
                        colnum += 1
                    rownum += 1
            elif data.ndim==1:
                self.view.spreadsheet.SetNumberCols(1)
                for el in data:
                    self.view.spreadsheet.AppendRows(1)
                    self.view.spreadsheet.SetCellValue(rownum, 0, str(el))
                    rownum += 1
        else:
            self.view.Destroy()