"""datapanel_model.py - model for the datapanel UI element

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
import os

class DataPanelModel(object):
    """Model for the DataPanel"""

    def __init__(self, controller):
        self.controller = controller

    def find_data(self):
        """Returns a list of the files found in the data folder"""
        data_list = []
        for root, dirs, files in os.walk(pathfinder.data_path()):
            for name in files:
                data_list.append(os.path.join(root, name))
        return data_list