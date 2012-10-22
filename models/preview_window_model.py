"""preview_window_model.py - model for the PreviewWindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from models import dataio
import numpy as np

__author__ = 'Chris R. Coughlin'

class PreviewWindowModel(object):
    """Model for the PreviewWindow"""

    def __init__(self, controller, data_file):
        self.controller = controller
        self.data_file = data_file
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = np.copy(new_data)

    def load_data(self):
        """Loads the data from the instance's data file"""
        self._data = dataio.get_data(self.data_file)

    def slice_data(self, slice_idx):
        """Sets the 3D self.data to a single 2D slice."""
        if self._data is not None:
            if self._data.ndim == 3:
                self._data = self._data[:, :, slice_idx]