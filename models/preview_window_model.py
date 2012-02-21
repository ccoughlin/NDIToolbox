"""preview_window_model.py - model for the PreviewWindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from models import mainmodel

__author__ = 'Chris R. Coughlin'

class PreviewWindowModel(object):
    """Model for the PreviewWindow"""

    def __init__(self, controller, data_file, **read_text_params):
        self.controller = controller
        self.data_file = data_file
        self.read_parameters = read_text_params
        self.data = None

    def load_data(self):
        """Loads the data from the instance's data file"""
        self.data = mainmodel.get_data(self.data_file, **self.read_parameters)