"""datapanel.py - creates the NDE Data wxPython panel for the A7117 UI

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import views.ui_defaults as ui_defaults
from controllers.datapanel_ctrl import DataPanelController

import wx
#import wx.aui

class DataPanel(wx.Panel):
    """Defines the wxPython panel used to display NDE Data"""

    def __init__(self, parent):
        self.parent = parent
        self.controller = DataPanelController(self)
        wx.Panel.__init__(self, id=wx.ID_ANY, name='', parent=self.parent)
        self.init_ui()

    @property
    def data(self):
        return self.controller.data

    def init_ui(self):
        """Generates the data panel"""
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.data_tree = wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
        self.data_tree_root = self.data_tree.AddRoot("Data")
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.controller.on_tree_selection_changed, self.data_tree)
        self.controller.populate_tree()
        self.panel_sizer.Add(self.data_tree, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                             ui_defaults.widget_margin)
        self.figure_bmp = wx.StaticBitmap(self, wx.ID_ANY, bitmap=wx.NullBitmap,
                                          pos=wx.DefaultPosition, size=wx.DefaultSize)
        self.panel_sizer.Add(self.figure_bmp, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                             ui_defaults.widget_margin)
        self.SetSizer(self.panel_sizer)




  