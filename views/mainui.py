"""mainui.py - primary wxPython user interface element

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import views.datapanel as datapanel
import views.thumbnail_panel as thumbnailpanel
import controllers.mainui_ctrl as ctrl
import wx
import wx.aui

class UI(wx.Frame):
    """Primary user interface"""

    def __init__(self):
        self.parent = None
        self.controller = ctrl.MainUIController(self)
        wx.Frame.__init__(self, id=wx.ID_ANY, name='', parent=self.parent,
                          size=(300, 600), title='A7117 NDE')
        self.SetPosition(self.controller.get_default_position())
        self.MinSize = (300, 400)
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.init_menu()
        self.init_ui()
        self.Bind(wx.EVT_CLOSE, self.controller.on_quit)

    def init_menu(self):
        """Creates the main application menu"""
        self.menubar = wx.MenuBar()
        self.init_file_menu()
        self.init_tools_menu()
        self.init_help_menu()
        self.SetMenuBar(self.menubar)

    def init_file_menu(self):
        """Creates the File menu"""
        self.file_mnu = wx.Menu()
        dicom_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Import DICOM/DICONDE...",
                                 help="Imports a DICOM / DICONDE data file")
        self.file_mnu.AppendItem(dicom_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_import_dicom, id=dicom_mnui.GetId())
        quit_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="E&xit\tCTRL+X",
                                help="Exit The Program")
        self.file_mnu.AppendItem(quit_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_quit, id=quit_mnui.GetId())
        self.menubar.Append(self.file_mnu, "&File")

    def init_tools_menu(self):
        """Creates the Tools menu"""
        self.tool_mnu = wx.Menu()
        podtk_mnui = wx.MenuItem(self.tool_mnu, wx.ID_ANY, text="POD Toolkit",
                                 help="Runs the Probability Of Detection Toolkit")
        self.tool_mnu.AppendItem(podtk_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_run_podtk, id=podtk_mnui.GetId())
        self.menubar.Append(self.tool_mnu, "&Tools")

    def init_help_menu(self):
        """Creates the Help menu"""
        self.help_mnu = wx.Menu()
        about_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="About This Program...",
                                 help="About This Program")
        self.help_mnu.AppendItem(about_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about, id=about_mnui.GetId())
        license_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="License Information...",
                                   help="License Information")
        self.help_mnu.AppendItem(license_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about_license, id=license_mnui.GetId())
        about_tri_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text='About TRI/Austin...',
                                     help="About TRI/Austin's NDE Division")
        self.help_mnu.AppendItem(about_tri_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about_tri, id=about_tri_mnui.GetId())
        about_icons_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="About Axialis Icons...",
                                       help="About the Axialis icons used in this project")
        self.help_mnu.AppendItem(about_icons_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about_icons, id=about_icons_mnui.GetId())
        self.menubar.Append(self.help_mnu, "&Help")

    def init_ui(self):
        """Creates the user interface"""
        self.init_tb()
        self.data_panel = datapanel.DataPanel(self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.controller.on_data_select,
                  self.data_panel.data_tree)
        self._mgr.AddPane(self.data_panel, wx.aui.AuiPaneInfo().
        Name("data_panel").Caption("NDE Data").Center().CloseButton(False).
        MinimizeButton(True).MaximizeButton(True).Floatable(True).
        MinSize(wx.Size(300, 50)).Dockable(True))
        self.thumbnail_panel = thumbnailpanel.ThumbnailPanel(self)
        self.controller.set_thumb(panel=self.thumbnail_panel, data_file=self.data_panel.data,
                                  enable=False)
        self._mgr.AddPane(self.thumbnail_panel, wx.aui.AuiPaneInfo().
        Name("thumbnail_panel").Caption("Preview Plot").MinSize(wx.Size(300, 300)).
        Bottom().CloseButton(False).MinimizeButton(True).MaximizeButton(True).
        Floatable(True).Dockable(True))
        self.SetIcon(self.controller.get_icon())
        self._mgr.Update()

    def init_tb(self):
        """Creates the toolbar"""
        self.toolbar = self.CreateToolBar(wx.TB_FLAT | wx.TB_NODIVIDER | wx.NO_BORDER)
        self.toolbar.SetToolBitmapSize((16, 16))
        # Toggle button to enable / disable automatic previews of data
        self.gen_bitmaps_tool = self.toolbar.AddCheckTool(id=wx.ID_ANY,
                                                          shortHelp='Enable Data Thumbnails',
                                                          bitmap=self.controller.get_bitmap(
                                                              'Picture.png'))
        self.toolbar.ToggleTool(self.gen_bitmaps_tool.GetId(),
                                self.controller.get_preview_state())
        self.Bind(wx.EVT_TOOL, self.controller.on_preview_toggle, self.gen_bitmaps_tool)
        # Refresh UI with contents of data folder
        self.refresh_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Refresh',
                                                           shortHelp='Refresh Data',
                                                           bitmap=self.controller.get_bitmap(
                                                               'Refresh.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_refresh_data, self.refresh_data_tool)
        # Add data to data folder
        self.add_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Add Data',
                                                       shortHelp='Add data to data folder',
                                                       bitmap=self.controller.get_bitmap(
                                                           'Plus.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_add_data, self.add_data_tool)
        # Remove data from data folder
        self.remove_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Remove Data',
                                                          shortHelp='Remove data from data folder',
                                                          bitmap=self.controller.get_bitmap(
                                                              'Minus.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_remove_data, self.remove_data_tool)
        # Preview data in spreadsheet
        self.preview_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Preview Data',
                                                           shortHelp='Preview data in spreadsheet',
                                                           bitmap=self.controller.get_bitmap(
                                                               'Table.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_preview_data, self.preview_data_tool)
        # Plot data
        self.plot_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'X-Y Plot',
                                                        shortHelp='Generates X-Y plot of selected'\
                                                                  ' data'
                                                        ,
                                                        bitmap=self.controller.get_bitmap(
                                                            'Stats2.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_plot_data, self.plot_data_tool)
        # Image plot of data
        self.imageplot_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Image Plot',
                                                             shortHelp='Generates image plot of selected data'
                                                             ,
                                                             bitmap=self.controller.get_bitmap(
                                                                 'imgplt.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_imageplot_data, self.imageplot_data_tool)
        self.disable_data_tools()
        self.toolbar.Realize()

    # Utility Functions
    def disable_data_tools(self):
        """Disables toolbar buttons that operate on a selected data file"""
        self.enable_data_tools(False)

    def enable_data_tools(self, enable=True):
        """Enables toolbar buttons that operate on a selected data file,
        or disables if enable is set to False."""
        self.toolbar.EnableTool(self.preview_data_tool.GetId(), enable)
        self.toolbar.EnableTool(self.plot_data_tool.GetId(), enable)
        self.toolbar.EnableTool(self.imageplot_data_tool.GetId(), enable)


def main():
    app = wx.PySimpleApp()
    ui = UI()
    ui.Show(True)
    app.MainLoop()

if __name__ == "__main__":
    main()