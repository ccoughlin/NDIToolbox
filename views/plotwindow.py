""" plotwindow.py - wxPython control for displaying matplotlib plots

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import ui_defaults
from controllers import pathfinder
from controllers.plotwindow_ctrl import PlotWindowController
import os.path
import wx
import wx.lib.dialogs as dlg
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx
from matplotlib.widgets import Cursor
import matplotlib.cm as cm

class PlotWindow(wx.Frame):
    """Basic wxPython UI element for displaying matplotlib plots"""

    def __init__(self, parent, data_file):
        self.parent = parent
        self.data_file = data_file
        self.controller = PlotWindowController(self)
        self.title = 'Plot - {0}'.format(os.path.basename(self.data_file))
        wx.Frame.__init__(self, id=wx.ID_ANY, parent=self.parent, title=self.title)
        self.init_menu()
        self.init_ui()
        self.axes_grid = True
        self.controller.load_data(self.data_file)
        self.plot(self.controller.data)

    @property
    def data(self):
        return self.controller.data

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
        #self.cursor = Cursor(self.axes, useblit=True, color='green', alpha=0.5, linestyle='--', linewidth=2)
        self.sizer.Add(self.canvas, 1, ui_defaults.sizer_flags, 0)
        self.add_toolbar()
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
            self.sizer.Add(self.toolbar, 0, wx.LEFT|wx.EXPAND, 0)
        self.toolbar.update()

    def init_menu(self):
        """Creates the main menu"""
        self.menubar = wx.MenuBar()
        self.init_plot_menu()
        self.init_ops_menu()
        self.init_scripts_menu()
        self.init_help_menu()
        self.SetMenuBar(self.menubar)

    def init_plot_menu(self):
        """Creates the Plot menu"""
        self.plot_mnu = wx.Menu()
        plottitle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set Plot Title",
                                     help="Set Plot Title")
        self.Bind(wx.EVT_MENU, self.on_set_plottitle, id=plottitle_mnui.GetId())
        self.plot_mnu.AppendItem(plottitle_mnui)
        xlbl_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set X Axis Label",
                                help="Set X Axis Label")
        self.Bind(wx.EVT_MENU, self.on_set_xlabel, id=xlbl_mnui.GetId())
        self.plot_mnu.AppendItem(xlbl_mnui)
        ylbl_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set Y Axis Label",
                                help="Set Y Axis Label")
        self.Bind(wx.EVT_MENU, self.on_set_ylabel, id=ylbl_mnui.GetId())
        self.plot_mnu.AppendItem(ylbl_mnui)
        gridtoggle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Toggle Grid",
                                      help="Turns grid on or off")
        self.plot_mnu.AppendItem(gridtoggle_mnui)
        self.Bind(wx.EVT_MENU, self.on_toggle_grid, id=gridtoggle_mnui.GetId())
        self.menubar.Append(self.plot_mnu, "&Plot")

    def init_ops_menu(self):
        """Creates the Operations menu"""
        self.ops_mnu = wx.Menu()
        self.revert_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text='Revert To Original',
                                       help='Revert to original data set')
        self.Bind(wx.EVT_MENU, self.on_revert, id=self.revert_mnui.GetId())
        self.ops_mnu.AppendItem(self.revert_mnui)
        self.init_specific_ops_menu()
        self.menubar.Append(self.ops_mnu, '&Operations')

    def init_specific_ops_menu(self):
        """Creates any plot-specific Operations menu items"""
        self.rect_mnu = wx.Menu() # Rectification operations
        self.norect_mnui = wx.MenuItem(self.rect_mnu, wx.ID_ANY, text="None",
                                       help="No Rectification")
        self.Bind(wx.EVT_MENU, self.on_rectify, id=self.norect_mnui.GetId())
        self.rect_mnu.AppendItem(self.norect_mnui)
        self.fullrect_mnui = wx.MenuItem(self.rect_mnu, wx.ID_ANY, text="Full",
                                         help="Full Rectification")
        self.Bind(wx.EVT_MENU, self.on_rectify, id=self.fullrect_mnui.GetId())
        self.rect_mnu.AppendItem(self.fullrect_mnui)
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Rectify', self.rect_mnu)

        self.gate_mnu = wx.Menu() # Gates operations
        for gate_idx, params in self.controller.gates.items():
            gate_lbl = params[0]
            gate_id = params[1]
            gate_desc = "Applies a {0} gate function to the data".format(gate_lbl)
            gate_mnui = wx.MenuItem(self.gate_mnu, id=gate_id, text=gate_lbl, help=gate_desc)
            self.gate_mnu.AppendItem(gate_mnui)
            self.Bind(wx.EVT_MENU, self.on_apply_gate, id=gate_mnui.GetId())
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Gates', self.gate_mnu)

    def init_scripts_menu(self):
        pass

    def init_help_menu(self):
        pass

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
            # matplotlib forgets settings with replots -
            # save current values to reset after the replot
            titles = self.get_titles()
            if 2 in data.shape:
                self.axes.plot(data[0], data[1])
            elif data.ndim == 1:
                self.axes.plot(data)
            self.set_titles(plot=titles['plot'], x=titles['x'], y=titles['y'])
            self.axes.grid(self.axes_grid)

    # Event Handlers
    def on_revert(self, evt):
        """Handles request to revert to original data set"""
        self.controller.revert_data()
        self.axes.hold()
        self.plot(self.controller.data)
        self.refresh_plot()
        self.axes.hold()

    def on_toggle_grid(self, evt):
        """Toggles the plot's grid on or off"""
        self.axes.grid()
        self.axes_grid = not self.axes_grid
        self.refresh_plot()

    def on_set_xlabel(self, evt):
        """Handles the set x-axis label event"""
        label_dlg = wx.TextEntryDialog(parent=self, message="Enter a new label for the X-Axis",
                                       caption="Set X Axis Label",
                                       defaultValue=self.get_titles()['x'])
        if label_dlg.ShowModal() == wx.ID_OK:
            self.set_titles(x=label_dlg.GetValue())

    def on_set_ylabel(self, evt):
        """Handles the set y-axis label event"""
        label_dlg = wx.TextEntryDialog(parent=self, message="Enter a new label for the Y-Axis",
                                       caption="Set Y Axis Label",
                                       defaultValue=self.get_titles()['y'])
        if label_dlg.ShowModal() == wx.ID_OK:
            self.set_titles(y=label_dlg.GetValue())

    def on_set_plottitle(self, evt):
        """Handles the set x-axis label event"""
        label_dlg = wx.TextEntryDialog(parent=self, message="Enter a new title for the plot",
                                       caption="Set Plot Title",
                                       defaultValue=self.get_titles()['plot'])
        if label_dlg.ShowModal() == wx.ID_OK:
            self.set_titles(plot=label_dlg.GetValue())

    def OnPaint(self, evt):
        """Handles wxPython paint event"""
        self.refresh_plot()
        evt.Skip()

    def on_rectify(self, evt):
        """Handles request to apply or remove rectification"""
        pass

    def on_apply_gate(self, evt):
        """Handles request to apply window function ('gate' in UT)
        to data"""
        self.axes.hold()
        self.controller.apply_gate(evt.GetId())
        self.plot(self.data)
        self.refresh_plot()
        self.axes.hold()

    def refresh_plot(self):
        """Forces plot to redraw itself"""
        self.canvas.draw()

    def get_titles(self):
        """Returns the current titles for the plot, x and y axes as a dict with
        keys 'plot', 'x', 'y'."""
        titles = {'plot': self.axes.get_title(),
                  'x': self.axes.get_xlabel(),
                  'y': self.axes.get_ylabel()}
        return titles

    def set_titles(self, plot=None, x=None, y=None):
        """Sets one or more of plot, x, or y axis titles to specified
        string.  If not specified, title is left unchanged."""
        if plot:
            self.axes.set_title(plot)
        if x:
            self.axes.set_xlabel(x)
        if y:
            self.axes.set_ylabel(y)
        self.refresh_plot()


class ImgPlotWindow(PlotWindow):
    """Specialized PlotWindow for handling imgplots"""

    def init_specific_ops_menu(self):
        pass