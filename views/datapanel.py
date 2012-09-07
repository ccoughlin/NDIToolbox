"""datapanel.py - creates the NDE Data wxPython panel for the NDIToolbox UI

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import views.ui_defaults as ui_defaults
from controllers.datapanel_ctrl import DataPanelController
from controllers import pathfinder, open_file
from models.mainmodel import get_logger
import wx
import os.path

module_logger = get_logger(__name__)

class DataPanel(wx.Panel):
    """Defines the wxPython panel used to display NDE Data"""

    def __init__(self, parent):
        self.parent = parent
        self.controller = DataPanelController(self)
        wx.Panel.__init__(self, id=wx.ID_ANY, name='', parent=self.parent)
        self.init_ui()
        module_logger.info("Successfully initialized DataPanel.")
        self.populate()

    @property
    def data(self):
        return self.controller.data

    def populate(self):
        """Retrieves the list of data files"""
        module_logger.info("Retrieving list of data files from controller.")
        self.controller.populate_tree()

    def init_ui(self):
        """Generates the data panel"""
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.data_tree = wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
        self.data_tree_root = self.data_tree.AddRoot(pathfinder.data_path())
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.controller.on_tree_selection_changed,
                  self.data_tree)
        self.data_tree.Bind(wx.EVT_RIGHT_DOWN, self.init_popup_menu)
        self.panel_sizer.Add(self.data_tree, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                             ui_defaults.widget_margin)
        self.figure_bmp = wx.StaticBitmap(self, wx.ID_ANY, bitmap=wx.NullBitmap,
                                          pos=wx.DefaultPosition, size=wx.DefaultSize)
        self.panel_sizer.Add(self.figure_bmp, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                             ui_defaults.widget_margin)
        self.SetSizer(self.panel_sizer)


    def init_popup_menu(self, evt):
        """Generates the contextual (right-click) menu"""
        self.PopupMenu(DataPanelContextMenu(self), evt.GetPosition())


class DataPanelContextMenu(wx.Menu):
    """Context (right-click) menu for DataPanels"""

    def __init__(self, parent):
        super(DataPanelContextMenu, self).__init__()
        self.parent = parent
        self.init_menu()

    def init_menu(self):
        """Creates the contextual menu"""
        self.browse_mnui = wx.MenuItem(self, wx.ID_ANY, "Browse To Folder")
        self.Bind(wx.EVT_MENU, self.on_browse, self.browse_mnui)
        self.AppendItem(self.browse_mnui)

    def on_browse(self, evt):
        """Handles request to open data folder.
        If a data file is not selected in the parent,
        opens the current user's root data folder instead."""
        if self.parent.data is None:
            browse_fldr = pathfinder.data_path()
        else:
            browse_fldr = os.path.dirname(self.parent.data)
        try:
            open_file.open_file(browse_fldr)
        except IOError as err: # file not found
            module_logger.error("Unable to find folder: {0}".format(err))
            err_msg = "Unable to find folder '{0}'.\nPlease ensure the folder exists.".format(browse_fldr)
            err_dlg = wx.MessageDialog(self.parent, message=err_msg,
                                       caption="Unable To Open Folder", style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()
        except OSError as err: # other OS error
            module_logger.error("Unable to browse to data folder (OS error): {0}".format(err))
            err_msg = "Unable to browse to data folder, error reported was:\n{0}".format(err)
            err_dlg = wx.MessageDialog(self.parent, message=err_msg,
                                       caption="Unable To Open Folder", style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()


  