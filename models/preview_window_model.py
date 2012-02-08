"""preview_window_model.py - model for the PreviewWindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from models import mainmodel

__author__ = 'Chris R. Coughlin'

def load_data_wrapper(data_filename, plugin_queue, read_parameters):
    """multiprocessing wrapper function to read large data
    files and send them through the specified Pipe instance."""
    data = mainmodel.get_data(data_filename, **read_parameters)
    plugin_queue.put(data)


class PreviewWindowModel(object):
    """Model for the PreviewWindow"""

    def __init__(self, controller, data_file, **read_text_params):
        self.controller = controller
        self.data_file = data_file
        self.read_parameters = read_text_params

    def load_data(self):
        """Loads the data from the instance's data file"""
        return mainmodel.get_data(self.data_file, **self.read_parameters)