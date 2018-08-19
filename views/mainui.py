"""mainui.py - primary wxPython user interface element

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import views.datapanel as datapanel
import views.thumbnail_panel as thumbnailpanel
import controllers.mainui_ctrl as ctrl
import wx
import wx.aui


class FileDropTarget(wx.FileDropTarget):

    def __init__(self, window):
        super(FileDropTarget, self).__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.controller.select_import_function(filenames[0])


class UI(wx.Frame):
    """Primary user interface"""

    def __init__(self):
        self.parent = None
        self.controller = ctrl.MainUIController(self)
        wx.Frame.__init__(self, id=wx.ID_ANY, name='', parent=self.parent,
                          size=(300, 600), title='NDIToolbox')
        self.SetPosition(self.controller.get_default_position())
        self.MinSize = (300, 400)
        self.SetSize(self.controller.get_window_size())
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.init_menu()
        self.init_ui()
        self.controller.verify_userpath()
        self.controller.verify_imports()
        self.Bind(wx.EVT_CLOSE, self.controller.on_quit)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.controller.on_window_destroy)

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
        self.import_mnu = wx.Menu()
        hdf5_mnui = wx.MenuItem(self.import_mnu, wx.ID_ANY, text="HDF5 File...",
                                helpString="Copies an HDF5 file to your NDIToolbox data folder")
        self.import_mnu.AppendItem(hdf5_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_import_hdf5, id=hdf5_mnui.GetId())
        txt_mnui = wx.MenuItem(self.import_mnu, wx.ID_ANY, text="Text File (CSV, etc.)...",
                               helpString="Imports delimited ASCII data file")
        self.import_mnu.AppendItem(txt_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_import_text, id=txt_mnui.GetId())
        csc_mnui = wx.MenuItem(self.import_mnu, wx.ID_ANY, text="UTWin CScan (.csc)...",
                               helpString="Imports a .csc file")
        self.import_mnu.AppendItem(csc_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_import_csc, id=csc_mnui.GetId())
        sdt_mnui = wx.MenuItem(self.import_mnu, wx.ID_ANY, text="Winspect 6/7 CScan (.sdt)...",
                               helpString="Imports a .sdt file")
        self.import_mnu.AppendItem(sdt_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_import_sdt, id=sdt_mnui.GetId())
        dicom_mnui = wx.MenuItem(self.import_mnu, wx.ID_ANY, text="DICOM/DICONDE...",
                                 helpString="Imports a DICOM / DICONDE data file")
        self.import_mnu.AppendItem(dicom_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_import_dicom, id=dicom_mnui.GetId())
        img_mnui = wx.MenuItem(self.import_mnu, wx.ID_ANY, text="Image...",
                               helpString="Imports an image file")
        self.Bind(wx.EVT_MENU, self.controller.on_import_image, id=img_mnui.GetId())
        self.import_mnu.AppendItem(img_mnui)
        self.file_mnu.AppendMenu(wx.ID_ANY, 'Import...', self.import_mnu)
        self.file_mnu.AppendSeparator()
        browsedata_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Show Data Folder",
                                      helpString="Opens the local storage folder")
        self.file_mnu.AppendItem(browsedata_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_browse_userpath, id=browsedata_mnui.GetId())
        self.file_mnu.AppendSeparator()
        quit_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="E&xit\tCTRL+X",
                                helpString="Exit The Program")
        self.file_mnu.AppendItem(quit_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_quit, id=quit_mnui.GetId())
        self.menubar.Append(self.file_mnu, "&File")

    def init_tools_menu(self):
        """Creates the Tools menu"""
        self.tool_mnu = wx.Menu()
        podtk_mnui = wx.MenuItem(self.tool_mnu, wx.ID_ANY, text="POD Toolkit",
                                 helpString="Runs the Probability Of Detection Toolkit")
        self.tool_mnu.AppendItem(podtk_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_run_podtk, id=podtk_mnui.GetId())
        self.prefs_mnu = wx.Menu() # Preferences Menu
        userpath_mnui = wx.MenuItem(self.prefs_mnu, wx.ID_ANY, text="Choose Data Folder...",
                                    helpString="Specify the local storage folder")
        self.prefs_mnu.AppendItem(userpath_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_choose_userpath, id=userpath_mnui.GetId())
        log_mnui = wx.MenuItem(self.prefs_mnu, wx.ID_ANY, text="Choose Logging Level...",
                                    helpString="Specify the severity of events recorded in the application log")
        self.prefs_mnu.AppendItem(log_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_choose_loglevel, id=log_mnui.GetId())
        self.tool_mnu.AppendMenu(wx.ID_ANY, 'Preferences', self.prefs_mnu)
        self.tool_mnu.AppendSeparator()
        gc_mnui = wx.MenuItem(self.tool_mnu, wx.ID_ANY, text="Free Memory...",
                              helpString="Attempt to free up memory by scheduling garbage collection")
        self.tool_mnu.AppendItem(gc_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_gc, id=gc_mnui.GetId())
        self.menubar.Append(self.tool_mnu, "&Tools")

    def init_help_menu(self):
        """Creates the Help menu"""
        self.help_mnu = wx.Menu()
        help_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="Help Topics",
                                helpString="Opens the help documentation in your web browser")
        self.help_mnu.AppendItem(help_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_help, id=help_mnui.GetId())
        quickstart_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="Getting Started",
                                      helpString="Opens the Getting Started Guide")
        self.help_mnu.AppendItem(quickstart_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_quickstart, id=quickstart_mnui.GetId())

        self.plugins_mnu = wx.Menu()
        plugins_mnui = wx.MenuItem(self.plugins_mnu, wx.ID_ANY, text="Using Plugins",
                                   helpString="Opens introduction to using NDIToolbox plugins")
        self.plugins_mnu.AppendItem(plugins_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_plugins, id=plugins_mnui.GetId())
        plugins_dev_mnui = wx.MenuItem(self.plugins_mnu, wx.ID_ANY, text="Writing Plugins",
                                       helpString="Opens introduction to writing NDIToolbox plugins")
        self.plugins_mnu.AppendItem(plugins_dev_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_plugins_dev, id=plugins_dev_mnui.GetId())
        plugins_samples_mnui = wx.MenuItem(self.plugins_mnu, wx.ID_ANY, text="Examples",
                                           helpString="Opens examples of NDIToolbox plugins")
        self.plugins_mnu.AppendItem(plugins_samples_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_plugins_samples, id=plugins_samples_mnui.GetId())
        self.help_mnu.AppendMenu(wx.ID_ANY, "NDIToolbox Plugins", self.plugins_mnu)
        self.help_mnu.AppendSeparator()
        about_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="About This Program...",
                                 helpString="About This Program")
        self.help_mnu.AppendItem(about_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about, id=about_mnui.GetId())
        license_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="License Information...",
                                   helpString="License Information")
        self.help_mnu.AppendItem(license_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about_license, id=license_mnui.GetId())
        about_tri_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text='About TRI/Austin...',
                                     helpString="About TRI/Austin's NDE Division")
        self.help_mnu.AppendItem(about_tri_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about_tri, id=about_tri_mnui.GetId())
        about_icons_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="About Axialis Icons...",
                                       helpString="About the Axialis icons used in this project")
        self.help_mnu.AppendItem(about_icons_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about_icons, id=about_icons_mnui.GetId())
        self.help_mnu.AppendSeparator()
        displaylog_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="Display Application Log...",
                                      helpString="Displays the NDIToolbox application log")
        self.Bind(wx.EVT_MENU, self.controller.on_display_log, id=displaylog_mnui.GetId())
        self.help_mnu.AppendItem(displaylog_mnui)
        clearlog_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="Clear Application Log",
                                    helpString="Deletes the NDIToolbox application log")
        self.Bind(wx.EVT_MENU, self.controller.on_clear_log, id=clearlog_mnui.GetId())
        self.help_mnu.AppendItem(clearlog_mnui)
        self.menubar.Append(self.help_mnu, "&Help")

    def init_ui(self):
        """Creates the user interface"""
        self.init_tb()
        self.data_panel = datapanel.DataPanel(self)
        file_drop_target = FileDropTarget(self)
        self.data_panel.SetDropTarget(file_drop_target)
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
        self.enable_preview_panel(self.controller.get_preview_state())
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, wx.WXK_NUMPAD_ADD, self.add_data_tool.GetId()),
                                              (wx.ACCEL_CTRL, ord('A'), self.add_data_tool.GetId())])
        self.SetAcceleratorTable(self.accel_tbl)
        self.SetIcon(self.controller.get_icon())
        self._mgr.Update()

    def init_tb(self):
        """Creates the toolbar"""
        self.toolbar = self.CreateToolBar(wx.TB_FLAT | wx.TB_NODIVIDER | wx.NO_BORDER)
        self.toolbar.SetToolBitmapSize((16, 16))
        # Toggle button to enable / disable automatic previews of data
        # Note: shortHelp should be accepted as an argument to AddCheckTool info
        # wxPython 4.0.3 but for some reason it is not recognized
        self.gen_bitmaps_tool = self.toolbar.AddCheckTool(toolId=wx.ID_ANY,
                                                          label="Thumbnails",
                                                          bitmap1=self.controller.get_bitmap('Picture.png'),
#                                                          shortHelp='Enable Data Thumbnails'
                                                          )
        self.toolbar.ToggleTool(self.gen_bitmaps_tool.GetId(),
                                self.controller.get_preview_state())
        self.Bind(wx.EVT_TOOL, self.controller.on_preview_toggle, self.gen_bitmaps_tool)
        # Refresh UI with contents of data folder
        self.refresh_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Refresh',
                                                           shortHelp='Refresh Data',
                                                           bitmap=self.controller.get_bitmap('Refresh.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_refresh_data, self.refresh_data_tool)
        self.toolbar.AddSeparator()
        # Add data to data folder
        self.add_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Add Data',
                                                       shortHelp='Import data to data folder (CTRL-A)',
                                                       bitmap=self.controller.get_bitmap('Plus.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_add_data, self.add_data_tool)
        # Remove data from data folder
        self.remove_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Remove Data',
            shortHelp='Remove data from data folder',
            bitmap=self.controller.get_bitmap('Minus.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_remove_data, self.remove_data_tool)
        # Export slice
        self.export_slice_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Slice Data', shortHelp='Export a slice of data',
            bitmap=self.controller.get_bitmap('Slice.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_slice_data, self.export_slice_tool)
        self.toolbar.AddSeparator()
        # Display info about data
        self.data_info_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Information',
                                                        shortHelp='Display information about the selected data',
                                                        bitmap=self.controller.get_bitmap('Info.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_data_info, self.data_info_tool)
        # Export data to ASCII
        self.export_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Export Data',
                                                          shortHelp="Exports selected data to text file",
                                                          bitmap=self.controller.get_bitmap('Save.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_export_text, self.export_data_tool)

        # Preview data in spreadsheet
        self.preview_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Preview Data',
                                                           shortHelp='Preview data in spreadsheet',
                                                           bitmap=self.controller.get_bitmap('Table.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_preview_data, self.preview_data_tool)
        self.toolbar.AddSeparator()
        # Plot data
        self.plot_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'X-Y Plot',
                                                        shortHelp='Generates X-Y plot of selected data',
                                                        bitmap=self.controller.get_bitmap('Stats2.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_plot_data, self.plot_data_tool)
        # Image plot of data
        self.imageplot_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Image Plot',
                                                             shortHelp='Generates image plot of selected data',
                                                             bitmap=self.controller.get_bitmap('imgplt.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_imageplot_data, self.imageplot_data_tool)
        # MegaNDE plot of 3D data
        self.megaplot_data_tool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Mega Plot',
                                                            shortHelp='Generates A, B, and C scans of selected data',
                                                            bitmap=self.controller.get_bitmap('dsfplot16.png'))
        self.Bind(wx.EVT_TOOL, self.controller.on_megaplot_data, self.megaplot_data_tool)
        self.disable_data_tools()
        self.toolbar.Realize()

    # Utility Functions
    def disable_data_tools(self):
        """Disables toolbar buttons that operate on a selected data file"""
        self.enable_data_tools(False)

    def enable_data_tools(self, enable=True):
        """Enables toolbar buttons that operate on a selected data file,
        or disables if enable is set to False."""
        self.toolbar.EnableTool(self.data_info_tool.GetId(), enable)
        self.toolbar.EnableTool(self.export_data_tool.GetId(), enable)
        self.toolbar.EnableTool(self.remove_data_tool.GetId(), enable)
        self.toolbar.EnableTool(self.preview_data_tool.GetId(), enable)
        self.toolbar.EnableTool(self.plot_data_tool.GetId(), enable)
        self.toolbar.EnableTool(self.imageplot_data_tool.GetId(), enable)
        self.toolbar.EnableTool(self.megaplot_data_tool.GetId(), enable)
        self.toolbar.EnableTool(self.export_slice_tool.GetId(), enable)

    def enable_preview_panel(self, enable=True):
        """Shows or hides the plot thumbnail panel"""
        pane_info = self._mgr.GetPane("thumbnail_panel")
        if enable:
            pane_info.Bottom()
            pane_info.Show()
        else:
            pane_info.Hide()
        self._mgr.Update()

    def refresh(self):
        """Convenience function for outside classes to force
        a refresh of the list of available data files."""
        self.data_panel.populate()


def main():
    app = wx.PySimpleApp()
    ui = UI()
    ui.Show(True)
    app.MainLoop()

if __name__ == "__main__":
    main()
