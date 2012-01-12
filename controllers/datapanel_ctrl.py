"""datapanel_ctrl.py - controller for the DataPanel element

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
import os.path

class DataPanelController(object):
    """Controller for the DataPanel"""

    def __init__(self, view):
        self.view = view

    def populate_tree(self):
        """Populates the view's tree with the contents in the data folder."""
        self.clear_tree()
        for file in self.find_data():
            data_item = self.view.data_tree.AppendItem(self.view.data_tree_root,
                                                       os.path.basename(file))
            self.view.data_tree.SetPyData(data_item, file)

    def clear_tree(self):
        """Removes the contents of the view's data tree"""
        self.view.data_tree.DeleteChildren(self.view.data_tree_root)

    def find_data(self):
        """Returns a list of the files found in the data folder"""
        data_list = []
        for root, dirs, files in os.walk(pathfinder.data_path()):
            for name in files:
                data_list.append(os.path.join(root, name))
        return data_list