"""preview_window_model.py - model for the PreviewWindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from models import mainmodel

__author__ = 'Chris R. Coughlin'

class PreviewWindowModel(object):
    """Model for the PreviewWindow"""

    def __init__(self, controller, data_file):
        self.controller = controller
        self.data_file = data_file
        self.data = None

    def load_data(self):
        """Loads the data from the instance's data file"""
        self.data = mainmodel.get_data(self.data_file)

    def slice_data(self, slice_idx):
        """Sets the 3D self.data to a single 2D slice."""
        if self.data is not None:
            if self.data.ndim == 3:
                min_slice_idx = 0
                max_slice_idx = self.data.shape[2]-1
                self.data = self.data[:, :, slice_idx]