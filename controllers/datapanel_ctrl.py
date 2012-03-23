"""datapanel_ctrl.py - controller for the DataPanel element

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.datapanel_model import DataPanelModel
import os.path

class DataPanelController(object):
    """Controller for the DataPanel"""

    def __init__(self, view):
        self.view = view
        self.model = DataPanelModel(self)
        self.data = None

    def populate_tree(self):
        """Populates the view's tree with the contents in the data folder."""
        self.clear_tree()
        for file in self.model.find_data():
            data_item = self.view.data_tree.AppendItem(self.view.data_tree_root,
                                                       os.path.basename(file))
            self.view.data_tree.SetPyData(data_item, file)

    def clear_tree(self):
        """Removes the contents of the view's data tree"""
        self.view.data_tree.DeleteChildren(self.view.data_tree_root)

        # Event Handlers

    def on_tree_selection_changed(self, evt):
        """Updates the currently selected data set"""
        item = evt.GetItem()
        if item:
            self.data = self.view.data_tree.GetItemPyData(item)
        evt.Skip()