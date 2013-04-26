""" plotwindow.py - wxPython control for displaying matplotlib plots

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import ui_defaults
from controllers.plotwindow_ctrl import PlotWindowController, ImgPlotWindowController, MegaPlotWindowController
from models import workerthread
from models.mainmodel import get_logger
import wx
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx
import os.path
import Queue

module_logger = get_logger(__name__)

class PlotWindow(wx.Frame):
    """Basic wxPython UI element for displaying matplotlib plots"""

    def __init__(self, parent, data_file):
        self.parent = parent
        self.data_file = data_file
        self.controller = PlotWindowController(self, data_file)
        module_logger.info("Successfully initialized PlotWindow.")
        self.load_data()

    def has_data(self):
        """Returns True if data is not None"""
        return self.controller.data is not None

    def load_data(self):
        """Loads the data set and plots"""
        exception_queue = Queue.Queue()
        data_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                             target=self.controller.load_data)
        data_thd.start()
        while True:
            data_thd.join(0.125)
            if not data_thd.is_alive():
                try:
                    exc_type, exc = exception_queue.get(block=False)
                    module_logger.error("Unable to load data: {0}".format(exc))
                    err_msg = "An error occurred while loading data:\n{0}".format(exc)
                    if len(err_msg) > 150:
                        # Truncate lengthy error messages
                        err_msg = ''.join([err_msg[:150], "\n(continued)"])
                    err_dlg = wx.MessageDialog(self.parent, message=err_msg,
                                               caption="Unable To Load Data", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                except Queue.Empty:
                    pass
                break
            wx.GetApp().Yield(True)
        if self.has_data():
            self.title = 'Plot - {0}'.format(os.path.basename(self.data_file))
            wx.Frame.__init__(self, id=wx.ID_ANY, parent=self.parent, title=self.title)
            self.init_menu()
            self.init_ui()
            self.controller.plot(self.controller.data)

    def init_ui(self):
        """Creates the PlotWindow UI"""
        parent_x, parent_y = self.parent.GetPositionTuple()
        parent_w, parent_h = self.parent.GetSize()
        self.SetPosition((parent_x + parent_w + ui_defaults.widget_margin,
                          ui_defaults.widget_margin))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.figure)
        self.axes = self.figure.add_subplot(111, picker=True)
        self.axes.grid(True)
        #self.cursor = Cursor(self.axes, useblit=True, color='green', alpha=0.5, linestyle='--',
        # linewidth=2)
        self.sizer.Add(self.canvas, 1, ui_defaults.sizer_flags, 0)
        self.add_toolbar()
        self.SetIcon(self.parent.GetIcon())
        self.SetSizerAndFit(self.sizer)

    def add_toolbar(self):
        """Creates the matplotlib toolbar (zoom, pan/scroll, etc.)
        for the plot"""
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            self.SetToolBar(self.toolbar)
        else:
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            self.toolbar.SetSize(wx.Size(fw, th))
            self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND, 0)
        self.toolbar.update()

    def init_menu(self):
        """Creates the main menu"""
        self.menubar = wx.MenuBar()
        self.init_file_menu()
        self.init_plot_menu()
        self.init_ops_menu()
        self.init_tools_menu()
        self.init_help_menu()
        self.SetMenuBar(self.menubar)

    def init_file_menu(self):
        """Creates the File menu"""
        self.file_mnu = wx.Menu()
        savedata_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Save Current Data",
                                    help="Save current data to disk")
        self.Bind(wx.EVT_MENU, self.controller.on_save_data, id=savedata_mnui.GetId())
        self.file_mnu.AppendItem(savedata_mnui)
        close_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Close Window",
                                 help="Close the plot window")
        self.Bind(wx.EVT_MENU, self.controller.on_close, id=close_mnui.GetId())
        self.file_mnu.AppendItem(close_mnui)
        self.menubar.Append(self.file_mnu, "&File")

    def init_plot_menu(self):
        """Creates the Plot menu"""
        self.plot_mnu = wx.Menu()

        self.labels_mnu = wx.Menu() # Titles and Labels
        plottitle_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set Plot Title",
                                     help="Set Plot Title")
        self.Bind(wx.EVT_MENU, self.controller.on_set_plottitle, id=plottitle_mnui.GetId())
        self.labels_mnu.AppendItem(plottitle_mnui)
        xlbl_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set X Axis Label",
                                help="Set X Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_xlabel, id=xlbl_mnui.GetId())
        self.labels_mnu.AppendItem(xlbl_mnui)
        ylbl_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set Y Axis Label",
                                help="Set Y Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_ylabel, id=ylbl_mnui.GetId())
        self.labels_mnu.AppendItem(ylbl_mnui)
        self.plot_mnu.AppendMenu(wx.ID_ANY, 'Title And Labels', self.labels_mnu)

        gridtoggle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Toggle Grid",
                                      help="Turns grid on or off")
        self.plot_mnu.AppendItem(gridtoggle_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_toggle_grid, id=gridtoggle_mnui.GetId())
        self.menubar.Append(self.plot_mnu, "&Plot")

    def init_ops_menu(self):
        """Creates the Operations menu"""
        self.ops_mnu = wx.Menu()
        self.revert_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text='Revert To Original',
                                       help='Revert to original data set')
        self.Bind(wx.EVT_MENU, self.controller.on_revert, id=self.revert_mnui.GetId())
        self.ops_mnu.AppendItem(self.revert_mnui)
        self.init_specific_ops_menu()
        self.menubar.Append(self.ops_mnu, '&Operations')

    def init_specific_ops_menu(self):
        """Creates any plot-specific Operations menu items"""
        self.rect_mnu = wx.Menu() # Rectification operations
        self.fullrect_mnui = wx.MenuItem(self.rect_mnu, wx.ID_ANY, text="Full",
                                         help="Full Rectification")
        self.Bind(wx.EVT_MENU, self.controller.on_rectify, id=self.fullrect_mnui.GetId())
        self.rect_mnu.AppendItem(self.fullrect_mnui)
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Rectify', self.rect_mnu)

        self.gate_mnu = wx.Menu() # Gates operations
        for gate in self.controller.gates:
            gate_name = self.controller.gates[gate][0]
            gate_desc = "Applies a {0} gate function to the data".format(gate_name)
            gate_mnui = wx.MenuItem(self.gate_mnu, id=gate, text=gate_name, help=gate_desc)
            self.gate_mnu.AppendItem(gate_mnui)
            self.Bind(wx.EVT_MENU, self.controller.on_apply_gate, id=gate_mnui.GetId())
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Gates', self.gate_mnu)

    def init_tools_menu(self):
        """Initializes the Tools Menu (Plugins and external scripts)"""
        self.tools_mnu = wx.Menu()
        self.init_plugins_menu()
        self.menubar.Append(self.tools_mnu, '&Tools')

    def init_plugins_menu(self):
        """Initializes the Plugins menu"""
        # If the Plugins menu already exists,
        # delete and rebuild.  Used to refresh
        # list of available plugins after installing
        # a new one
        plugins_mnu_id = self.tools_mnu.FindItem("Plugins")
        if plugins_mnu_id != -1:
            self.tools_mnu.RemoveItem(self.tools_mnu.FindItemById(plugins_mnu_id))
        self.plugins_mnu = wx.Menu()
        plugins = self.controller.available_plugins
        for plugin_id, plugin in plugins.items():
            plugin_name = plugin[1].name
            plugin_description = plugin[1].description
            script_mnui = wx.MenuItem(self.tools_mnu, id=plugin_id, text=plugin_name,
                                      help=plugin_description)
            self.Bind(wx.EVT_MENU, self.controller.on_run_toolkit, id=script_mnui.GetId())
            self.plugins_mnu.AppendItem(script_mnui)
        self.plugins_mnu.AppendSeparator()
        install_plugin_mnui = wx.MenuItem(self.plugins_mnu, wx.ID_ANY, text="Install Plugin...",
                                          help="Install a local plugin")
        self.Bind(wx.EVT_MENU, self.controller.on_install_plugin, id=install_plugin_mnui.GetId())
        self.plugins_mnu.AppendItem(install_plugin_mnui)
        download_plugin_mnui = wx.MenuItem(self.plugins_mnu, wx.ID_ANY, text="Download Plugin...",
                                           help="Download and install a new plugin")
        self.Bind(wx.EVT_MENU, self.controller.on_download_plugin, id=download_plugin_mnui.GetId())
        self.plugins_mnu.AppendItem(download_plugin_mnui)
        self.tools_mnu.AppendMenu(wx.ID_ANY, "Plugins", self.plugins_mnu)

    def init_help_menu(self):
        pass


class ImgPlotWindow(PlotWindow):
    """Specialized PlotWindow for handling imgplots"""

    def __init__(self, parent, data_file):
        self.parent = parent
        self.data_file = data_file
        self.controller = ImgPlotWindowController(self, data_file)
        module_logger.info("Successfully initialized ImgPlotWindow.")
        self.load_data()

    def load_data(self):
        """Loads the data set and plots"""
        exception_queue = Queue.Queue()
        data_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                             target=self.controller.load_data)
        data_thd.start()
        while True:
            data_thd.join(0.125)
            if not data_thd.is_alive():
                try:
                    exc_type, exc = exception_queue.get(block=False)
                    module_logger.error("Unable to load data: {0}".format(exc))
                    err_msg = "An error occurred while loading data:\n{0}".format(exc)
                    if len(err_msg) > 150:
                        # Truncate lengthy error messages
                        err_msg = ''.join([err_msg[:150], "\n(continued)"])
                    err_dlg = wx.MessageDialog(self.parent, message=err_msg,
                                               caption="Unable To Load Data", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                except Queue.Empty:
                    pass
                break
            wx.GetApp().Yield(True)
        self.title = 'Plot - {0}'.format(os.path.basename(self.data_file))
        wx.Frame.__init__(self, id=wx.ID_ANY, parent=self.parent, title=self.title)
        self.init_menu()
        self.init_ui()
        self.controller.check_data_dims()
        self.controller.plot(self.controller.data)

    def init_plot_menu(self):
        """Creates the Plot menu"""
        self.plot_mnu = wx.Menu()

        self.labels_mnu = wx.Menu() # Titles and Labels
        plottitle_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set Plot Title",
                                     help="Set Plot Title")
        self.Bind(wx.EVT_MENU, self.controller.on_set_plottitle, id=plottitle_mnui.GetId())
        self.labels_mnu.AppendItem(plottitle_mnui)
        xlbl_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set X Axis Label",
                                help="Set X Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_xlabel, id=xlbl_mnui.GetId())
        self.labels_mnu.AppendItem(xlbl_mnui)
        ylbl_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set Y Axis Label",
                                help="Set Y Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_ylabel, id=ylbl_mnui.GetId())
        self.labels_mnu.AppendItem(ylbl_mnui)
        cbarlbl_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text='Set Colorbar Label',
                                   help='Set Colorbar Label')
        self.Bind(wx.EVT_MENU, self.controller.on_set_cbarlbl, id=cbarlbl_mnui.GetId())
        self.labels_mnu.AppendItem(cbarlbl_mnui)
        self.plot_mnu.AppendMenu(wx.ID_ANY, "Title And Labels", self.labels_mnu)

        self.colormaps_mnu = wx.Menu() # Colormaps
        self.preview_cmaps_mnui = wx.MenuItem(self.colormaps_mnu, wx.ID_ANY, text='Preview Colormaps',
                                              help='Preview available colormaps')
        self.Bind(wx.EVT_MENU, self.controller.on_preview_cmaps, id=self.preview_cmaps_mnui.GetId())
        self.colormaps_mnu.AppendItem(self.preview_cmaps_mnui)
        self.select_cmap_mnui = wx.MenuItem(self.colormaps_mnu, wx.ID_ANY, text='Select Colormap...',
                                            help='Selects colormap')
        self.Bind(wx.EVT_MENU, self.controller.on_select_cmap, id=self.select_cmap_mnui.GetId())
        self.colormaps_mnu.AppendItem(self.select_cmap_mnui)
        self.create_cmap_mnui = wx.MenuItem(self.colormaps_mnu, wx.ID_ANY, text='Create Colormap...',
                                           help='Create or edit a colormap')
        self.colormaps_mnu.AppendItem(self.create_cmap_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_create_cmap, id=self.create_cmap_mnui.GetId())
        self.plot_mnu.AppendMenu(wx.ID_ANY, "Colormaps", self.colormaps_mnu)

        gridtoggle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Toggle Grid",
                                      help="Turns grid on or off")
        self.plot_mnu.AppendItem(gridtoggle_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_toggle_grid, id=gridtoggle_mnui.GetId())
        self.menubar.Append(self.plot_mnu, "&Plot")

    def init_specific_ops_menu(self):
        """Implements imgplot-specific operations for the Operations menu"""
        self.manip_mnu = wx.Menu() # Data manipulations
        self.flip_mnu = wx.Menu() # Flip data
        self.flipud_mnui = wx.MenuItem(self.flip_mnu, wx.ID_ANY, text="Vertically")
        self.Bind(wx.EVT_MENU, self.controller.on_flipud, id=self.flipud_mnui.GetId())
        self.flip_mnu.AppendItem(self.flipud_mnui)
        self.fliplr_mnui = wx.MenuItem(self.flip_mnu, wx.ID_ANY, text="Horizontally")
        self.Bind(wx.EVT_MENU, self.controller.on_fliplr, id=self.fliplr_mnui.GetId())
        self.flip_mnu.AppendItem(self.fliplr_mnui)
        self.manip_mnu.AppendMenu(wx.ID_ANY, 'Flip', self.flip_mnu)
        self.rot_mnu = wx.Menu() # Rotate data
        self.rot90ccw_mnui = wx.MenuItem(self.rot_mnu, wx.ID_ANY, text="90 Degrees CCW")
        self.Bind(wx.EVT_MENU, self.controller.on_rot90ccw, id=self.rot90ccw_mnui.GetId())
        self.rot_mnu.AppendItem(self.rot90ccw_mnui)
        self.rot90cw_mnui = wx.MenuItem(self.rot_mnu, wx.ID_ANY, text="90 Degreees CW")
        self.Bind(wx.EVT_MENU, self.controller.on_rot90cw, id=self.rot90cw_mnui.GetId())
        self.rot_mnu.AppendItem(self.rot90cw_mnui)
        self.rot180_mnui = wx.MenuItem(self.rot_mnu, wx.ID_ANY, text="180 Degrees")
        self.Bind(wx.EVT_MENU, self.controller.on_rot180, id=self.rot180_mnui.GetId())
        self.rot_mnu.AppendItem(self.rot180_mnui)
        self.manip_mnu.AppendMenu(wx.ID_ANY, 'Rotate', self.rot_mnu)
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Flip/Rotate Data', self.manip_mnu)
        self.detrend_mnu = wx.Menu() # Detrending menu
        self.detrend_constantx_mnui = wx.MenuItem(self.detrend_mnu, wx.ID_ANY,
                                                  text="Constant Horizontal")
        self.Bind(wx.EVT_MENU, self.controller.on_detrend_meanx,
                  id=self.detrend_constantx_mnui.GetId())
        self.detrend_mnu.AppendItem(self.detrend_constantx_mnui)
        self.detrend_constanty_mnui = wx.MenuItem(self.detrend_mnu, wx.ID_ANY,
                                                  text="Constant Vertical")
        self.Bind(wx.EVT_MENU, self.controller.on_detrend_meany,
                  id=self.detrend_constanty_mnui.GetId())
        self.detrend_mnu.AppendItem(self.detrend_constanty_mnui)
        self.detrend_linearx_mnui = wx.MenuItem(self.detrend_mnu, wx.ID_ANY,
                                                text="Linear Horizontal")
        self.Bind(wx.EVT_MENU, self.controller.on_detrend_linearx,
                  id=self.detrend_linearx_mnui.GetId())
        self.detrend_mnu.AppendItem(self.detrend_linearx_mnui)
        self.detrend_lineary_mnui = wx.MenuItem(self.detrend_mnu, wx.ID_ANY,
                                                text="Linear Vertical")
        self.Bind(wx.EVT_MENU, self.controller.on_detrend_lineary,
                  id=self.detrend_lineary_mnui.GetId())
        self.detrend_mnu.AppendItem(self.detrend_lineary_mnui)
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Detrend Data', self.detrend_mnu)
        self.transpose_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text="Transpose Data")
        self.Bind(wx.EVT_MENU, self.controller.on_transpose, id=self.transpose_mnui.GetId())
        self.ops_mnu.AppendItem(self.transpose_mnui)


class MegaPlotWindow(PlotWindow):
    """Specialized four-panel PlotWindow for displaying
    A, B, and C scans of a three-dimensional dataset"""

    def __init__(self, parent, data_file):
        self.parent = parent
        self.data_file = data_file
        self.controller = MegaPlotWindowController(self, data_file)
        module_logger.info("Successfully initialized MegaPlotWindow.")
        self.load_data()

    @property
    def axes(self):
        """Returns a tuple of all the view's axes"""
        return (self.ascan_axes, self.hbscan_axes,
                self.vbscan_axes, self.cscan_axes)

    def init_ui(self):
        """Creates the PlotWindow UI"""
        parent_x, parent_y = self.parent.GetPositionTuple()
        parent_w, parent_h = self.parent.GetSize()
        self.SetPosition((parent_x + parent_w + ui_defaults.widget_margin,
                          ui_defaults.widget_margin))
        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Controls for specifying (x,y,z) position in 3D dataset
        self.ctrl_panel = wx.Panel(self.main_panel)
        self.ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        info_lbl = wx.StaticText(self.ctrl_panel, wx.ID_ANY, u"Coordinates In Data:", wx.DefaultPosition,
                                 wx.DefaultSize)
        self.ctrl_sizer.Add(info_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags, ui_defaults.widget_margin)
        xpos_lbl = wx.StaticText(self.ctrl_panel, wx.ID_ANY, u"X Position", wx.DefaultPosition, wx.DefaultSize)
        self.ctrl_sizer.Add(xpos_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags, ui_defaults.widget_margin)
        self.xpos_sc = wx.SpinCtrl(self.ctrl_panel, wx.ID_ANY, value="", min=0, max=self.controller.data.shape[1] - 1)
        self.Bind(wx.EVT_SPINCTRL, self.controller.on_xy_change, self.xpos_sc)
        self.ctrl_sizer.Add(self.xpos_sc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        ypos_lbl = wx.StaticText(self.ctrl_panel, wx.ID_ANY, u"Y Position", wx.DefaultPosition, wx.DefaultSize)
        self.ctrl_sizer.Add(ypos_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags, ui_defaults.widget_margin)
        self.ypos_sc = wx.SpinCtrl(self.ctrl_panel, wx.ID_ANY, value="", min=0, max=self.controller.data.shape[0] - 1)
        self.Bind(wx.EVT_SPINCTRL, self.controller.on_xy_change, self.ypos_sc)
        self.ctrl_sizer.Add(self.ypos_sc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.slice_cb = wx.CheckBox(self.ctrl_panel, wx.ID_ANY, "Plot Z Index As C Scan", style=wx.ALIGN_RIGHT)
        self.slice_cb.SetToolTipString(u"Use the specified index in Z as the C Scan plot data")
        self.slice_cb.SetValue(True)
        self.ctrl_sizer.Add(self.slice_cb, ui_defaults.lbl_pct, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.slice_sc = wx.SpinCtrl(self.ctrl_panel, wx.ID_ANY, value="", min=0, max=self.controller.data.shape[2] - 1)
        self.Bind(wx.EVT_SPINCTRL, self.controller.on_sliceidx_change, self.slice_sc)
        slice_lbl = wx.StaticText(self.ctrl_panel, wx.ID_ANY, u"Slice Index", wx.DefaultPosition, wx.DefaultSize)
        self.ctrl_sizer.Add(slice_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags, ui_defaults.widget_margin)
        self.ctrl_sizer.Add(self.slice_sc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.ctrl_panel.SetSizerAndFit(self.ctrl_sizer)
        self.main_panel_sizer.Add(self.ctrl_panel, ui_defaults.lbl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.main_panel, wx.ID_ANY, self.figure)
        self.ascan_axes = self.figure.add_subplot(221)
        self.vbscan_axes = self.figure.add_subplot(222)
        self.hbscan_axes = self.figure.add_subplot(223)
        self.cscan_axes = self.figure.add_subplot(224)
        self.cscan_cursor = Cursor(self.cscan_axes, useblit=True, color="#4F6581", alpha=0.5)
        self.figure.canvas.mpl_connect("button_press_event", self.controller.on_click)
        self.main_panel_sizer.Add(self.canvas, 1, ui_defaults.sizer_flags, 0)
        self.navtools_cb = wx.CheckBox(self.main_panel, wx.ID_ANY, "Use Plot Navigation Tools")
        self.navtools_cb.SetValue(self.controller.get_navtools_config())
        self.navtools_cb.SetToolTipString("Check to use pan/zoom tools")
        self.Bind(wx.EVT_CHECKBOX, self.controller.on_check_navtools, self.navtools_cb)
        self.main_panel_sizer.Add(self.navtools_cb, ui_defaults.lbl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.add_toolbar()
        self.SetIcon(self.parent.GetIcon())
        self.main_panel.SetSizerAndFit(self.main_panel_sizer)
        self.sizer.Add(self.main_panel, 1, ui_defaults.sizer_flags, 0)
        self.SetSizerAndFit(self.sizer)

    def add_toolbar(self):
        """Creates the matplotlib toolbar (zoom, pan/scroll, etc.)
        for the plot"""
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            self.SetToolBar(self.toolbar)
        else:
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            self.toolbar.SetSize(wx.Size(fw, th))
            self.main_panel_sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND, 0)
        self.toolbar.update()
        self.toggle_toolbar()

    def toggle_toolbar(self):
        """Enables / disables the navigation toolbar and sets
        cursors accordingly."""
        if self.navtools_enabled():
            self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        else:
            self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
        self.toolbar.Enable(self.navtools_enabled())
        self.controller.set_navtools_config(self.navtools_enabled())

    def init_plot_menu(self):
        """Creates the Plot menu"""
        self.plot_mnu = wx.Menu()

        self.labels_mnu = wx.Menu() # Titles and Labels
        plottitle_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set Plot Title",
                                     help="Set Plot Title")
        self.Bind(wx.EVT_MENU, self.controller.on_set_plottitle, id=plottitle_mnui.GetId())
        self.labels_mnu.AppendItem(plottitle_mnui)
        xlbl_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set X Axis Label",
                                help="Set X Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_xlabel, id=xlbl_mnui.GetId())
        self.labels_mnu.AppendItem(xlbl_mnui)
        ylbl_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text="Set Y Axis Label",
                                help="Set Y Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_ylabel, id=ylbl_mnui.GetId())
        self.labels_mnu.AppendItem(ylbl_mnui)
        cbarlbl_mnui = wx.MenuItem(self.labels_mnu, wx.ID_ANY, text='Set Colorbar Label',
                                   help='Set Colorbar Label')
        self.Bind(wx.EVT_MENU, self.controller.on_set_cbarlbl, id=cbarlbl_mnui.GetId())
        self.labels_mnu.AppendItem(cbarlbl_mnui)
        self.plot_mnu.AppendMenu(wx.ID_ANY, "Title And Labels", self.labels_mnu)

        self.colormaps_mnu = wx.Menu() # Colormaps
        self.preview_cmaps_mnui = wx.MenuItem(self.colormaps_mnu, wx.ID_ANY, text='Preview Colormaps',
                                              help='Preview available colormaps')
        self.Bind(wx.EVT_MENU, self.controller.on_preview_cmaps, id=self.preview_cmaps_mnui.GetId())
        self.colormaps_mnu.AppendItem(self.preview_cmaps_mnui)
        self.select_cmap_mnui = wx.MenuItem(self.colormaps_mnu, wx.ID_ANY, text='Select Colormap...',
                                            help='Selects colormap')
        self.Bind(wx.EVT_MENU, self.controller.on_select_cmap, id=self.select_cmap_mnui.GetId())
        self.colormaps_mnu.AppendItem(self.select_cmap_mnui)
        self.create_cmap_mnui = wx.MenuItem(self.colormaps_mnu, wx.ID_ANY, text='Create Colormap...',
                                            help='Create or edit a colormap')
        self.colormaps_mnu.AppendItem(self.create_cmap_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_create_cmap, id=self.create_cmap_mnui.GetId())
        self.plot_mnu.AppendMenu(wx.ID_ANY, "Colormaps", self.colormaps_mnu)
        self.show_colorbar_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Show Colorbar",
                                              help="Show color scale in image plot", kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.controller.on_toggle_colorbar, id=self.show_colorbar_mnui.GetId())
        self.plot_mnu.AppendItem(self.show_colorbar_mnui)
        self.show_colorbar_mnui.Check(self.controller.get_colorbar_config())
        self.plot_conventional_bscans_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Plot Conventional B-scans",
                                                         help="Plot conventional 2D B-scans", kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.controller.on_change_bscans, id=self.plot_conventional_bscans_mnui.GetId())
        self.plot_mnu.AppendItem(self.plot_conventional_bscans_mnui)
        self.plot_conventional_bscans_mnui.Check(self.controller.conventional_bscans)
        gridtoggle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Toggle Grid",
                                      help="Turns grid on or off")
        self.plot_mnu.AppendItem(gridtoggle_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_toggle_grid, id=gridtoggle_mnui.GetId())
        self.menubar.Append(self.plot_mnu, "&Plot")

    def init_specific_ops_menu(self):
        """Creates any plot-specific Operations menu items"""
        self.setcscan_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text="Define C Scan",
                                         help="Specify function to generate C Scan")
        self.Bind(wx.EVT_MENU, self.controller.on_define_cscan, id=self.setcscan_mnui.GetId())
        self.ops_mnu.AppendItem(self.setcscan_mnui)
        self.rect_mnu = wx.Menu() # Rectification operations
        self.fullrect_mnui = wx.MenuItem(self.rect_mnu, wx.ID_ANY, text="Full",
                                         help="Full Rectification")
        self.Bind(wx.EVT_MENU, self.controller.on_rectify, id=self.fullrect_mnui.GetId())
        self.rect_mnu.AppendItem(self.fullrect_mnui)
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Rectify', self.rect_mnu)
        self.gate_mnu = wx.Menu() # Gates operations
        for gate in self.controller.gates:
            gate_name = self.controller.gates[gate][0]
            gate_desc = "Applies a {0} gate function to the data".format(gate_name)
            gate_mnui = wx.MenuItem(self.gate_mnu, id=gate, text=gate_name, help=gate_desc)
            self.gate_mnu.AppendItem(gate_mnui)
            self.Bind(wx.EVT_MENU, self.controller.on_apply_gate, id=gate_mnui.GetId())
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Gates', self.gate_mnu)

    def navtools_enabled(self):
        """Returns True if plot navigation bar is enabled"""
        return self.navtools_cb.IsChecked()

    @property
    def plot_conventional_bscans(self):
        """True if the Bscan plots should be conventional 2D imgplots vs. the original Megaplot 1D"""
        return self.plot_conventional_bscans_mnui.IsChecked()

    @plot_conventional_bscans.setter
    def plot_conventional_bscans(self, on=True):
        """Sets the use of conventional Bscans or the original 1D Megaplot Bscans"""
        self.plot_conventional_bscans_mnui.Check(on)

    @property
    def plot_linear_bscans(self):
        """True if the Bscan plots should be the original 1D Megaplot plots"""
        return not self.plot_conventional_bscans