"""plotwindow_ctrl.py - defines the controller for plotwindow.py

Chris R. Coughlin (TRI/Austin, Inc.)
"""
__author__ = 'Chris R. Coughlin'

from views import dialogs
from models import mainmodel
import pathfinder
import models.plotwindow_model as model
import matplotlib
from matplotlib import cm
import wx
import wx.lib.dialogs
from functools import wraps
import multiprocessing
import Queue

def replace_plot(fn):
    """Decorator function - runs the specified function and updates the plot.
    Designed to work with PlotWindowController instances.
    """
    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        if self.model.data is not None:
            self.view.axes.hold()
            fn(self, *args, **kwargs)
            self.plot(self.model.data)
            self.refresh_plot()
            self.view.axes.hold()
    return wrapped

def plugin_wrapper(plugin_cls, plugin_data, plugin_queue, plugin_cfg=None):
    """multiprocessing wrapper function, used to execute
    plugin run() method in separate process.  plugin_cls is the Plugin class
    to instantiate, plugin_data is the data to run the plugin on, and
    plugin_queue is the Queue instance the function should return the
    results in back to the caller.  If plugin_cfg is not None, it is
    supplied to the Plugin instance as its config dict.
    """
    plugin_instance = plugin_cls()
    plugin_instance.data = plugin_data
    if plugin_cfg is not None:
        plugin_instance.config = plugin_cfg
    plugin_instance.run()
    plugin_queue.put(plugin_instance.data)

class BasicPlotWindowController(object):
    """Base class for PlotWindows"""

    def __init__(self, view):
        self.view = view
        self.axes_grid = True
        self.model = model.BasicPlotWindowModel(self)
        self.init_plot_defaults()
        self.available_plugins = self.generate_plugin_dict()

    def init_plot_defaults(self):
        """Sets some basic matplotlib configuration parameters
        to sane defaults."""
        matplotlib.rcParams['font.size'] = 14
        matplotlib.rcParams['axes.titlesize'] = 12
        matplotlib.rcParams['axes.labelsize'] = 12
        matplotlib.rcParams['xtick.labelsize'] = 11
        matplotlib.rcParams['ytick.labelsize'] = 11

    @property
    def data(self):
        return self.model.data

    @property
    def original_data(self):
        return self.model.original_data

    def refresh_plot(self):
        """Forces plot to redraw itself"""
        self.view.canvas.draw()

    def on_run_plugin(self, evt):
        """Handles request to run a plugin"""
        self.run_plugin(evt.GetId())

    @replace_plot
    def run_plugin(self, requested_plugin_id):
        """Runs plugin with specified ID on current data set,
        replaces current data and refreshes plot"""
        for plugin_id, plugin in self.available_plugins.items():
            if requested_plugin_id == plugin_id:
                cfg = None
                plugin_name = plugin[0]
                available_plugins = self.get_plugins()
                plugin_names = [plugin[0] for plugin in available_plugins]
                plugin_classes = [plugin[1] for plugin in available_plugins]
                if plugin_name in plugin_names:
                    plugin_class = plugin_classes[plugin_names.index(plugin_name)]
                    plugin_instance = plugin_class()
                    plugin_instance.data = self.data
                if hasattr(plugin_instance, "config"):
                    cfg = self.configure_plugin_dlg(plugin_instance)
                    if cfg is not None:
                        plugin_instance.config = cfg
                plugin_queue = multiprocessing.Queue()
                plugin_process = multiprocessing.Process(target=plugin_wrapper,
                                                         args=(plugin_class, self.data, plugin_queue, cfg))
                plugin_process.daemon = True
                plugin_process.start()
                keepGoing = True
                # TODO: move progress dialog to dialogs module
                progress_dlg = wx.ProgressDialog("Running Plugin",
                                                 "Please wait, executing plugin...",
                                                 parent=self.view,
                                                 style=wx.PD_CAN_ABORT|wx.PD_APP_MODAL)
                while keepGoing:
                    wx.MilliSleep(100)
                    (keepGoing, skip) = progress_dlg.UpdatePulse()
                    try:
                        returned_data = plugin_queue.get(False)
                    except Queue.Empty:
                        continue
                    if returned_data is not None:
                        self.model.data = returned_data
                        break
                    if not keepGoing:
                        plugin_process.terminate()
                    wx.Yield()
                progress_dlg.Destroy()

    def on_close(self, evt):
        """Handles request to close plot window"""
        self.view.Destroy()

    def on_save_data(self, evt):
        """Handles request to save current data set to disk"""
        save_dlg = wx.FileDialog(self.view, message="Save File As...",
                                 defaultDir=pathfinder.data_path(), style=wx.SAVE|wx.OVERWRITE_PROMPT)
        if save_dlg.ShowModal() == wx.ID_OK:
            export_parameters = {'delimiter':','}
            mainmodel.save_data(save_dlg.GetPath(), self.data, **export_parameters)
        save_dlg.Destroy()

    def on_revert(self, evt):
        """Handles request to revert to original data set"""
        self.revert()

    def on_toggle_grid(self, evt):
        """Toggles the plot's grid on or off"""
        self.view.axes.grid()
        self.axes_grid = not self.axes_grid
        self.refresh_plot()

    def on_set_xlabel(self, evt):
        """Handles the set x-axis label event"""
        label_dlg = wx.TextEntryDialog(parent=self.view.parent, message="Enter a new label for the X-Axis",
                                       caption="Set X Axis Label",
                                       defaultValue=self.get_titles()['x'])
        if label_dlg.ShowModal() == wx.ID_OK:
            self.set_titles(x=label_dlg.GetValue())

    def on_set_ylabel(self, evt):
        """Handles the set y-axis label event"""
        label_dlg = wx.TextEntryDialog(parent=self.view.parent, message="Enter a new label for the Y-Axis",
                                       caption="Set Y Axis Label",
                                       defaultValue=self.get_titles()['y'])
        if label_dlg.ShowModal() == wx.ID_OK:
            self.set_titles(y=label_dlg.GetValue())

    def on_set_plottitle(self, evt):
        """Handles the set x-axis label event"""
        label_dlg = wx.TextEntryDialog(parent=self.view.parent, message="Enter a new title for the plot",
                                       caption="Set Plot Title",
                                       defaultValue=self.get_titles()['plot'])
        if label_dlg.ShowModal() == wx.ID_OK:
            self.set_titles(plot=label_dlg.GetValue())

    def get_titles(self):
        """Returns the current titles for the plot, x and y axes as a dict with
        keys 'plot', 'x', 'y'."""
        titles = {'plot': self.view.axes.get_title(),
                  'x': self.view.axes.get_xlabel(),
                  'y': self.view.axes.get_ylabel()}
        return titles

    def set_titles(self, plot=None, x=None, y=None):
        """Sets one or more of plot, x, or y axis titles to specified
        string.  If not specified, title is left unchanged."""
        if plot:
            self.view.axes.set_title(plot)
        if x:
            self.view.axes.set_xlabel(x)
        if y:
            self.view.axes.set_ylabel(y)
        self.refresh_plot()

    def OnPaint(self, evt):
        """Handles wxPython paint event"""
        self.refresh_plot()
        evt.Skip()

    def on_rectify(self, evt):
        """Handles request to apply rectification"""
        self.rectify_full()

    @replace_plot
    def revert(self):
        """Reverts data to original"""
        self.model.revert_data()

    def load_data(self, data_file):
        """Loads the data from the specified file name,
        returning True if the data were successfully loaded and
        False otherwise."""
        import_dlg = dialogs.ImportTextDialog(parent=self.view.parent)
        if import_dlg.ShowModal() == wx.ID_OK:
            readtext_parameters = import_dlg.get_import_parameters()
            self.model.original_data = mainmodel.get_data(data_file, **readtext_parameters)
            self.model.revert_data()
            return True
        else:
            return False

    def get_plugins(self):
        """Returns a list of the available A7117 plugins"""
        return self.model.get_plugins()

    def generate_plugin_dict(self):
        """Returns a dict (key = wx ID, val = plugin) suitable
        for inclusion in a Menu."""
        plugin_id = 1000
        plugins = {}
        for plugin in self.get_plugins():
            plugins[plugin_id] = plugin
            plugin_id += 1
        return plugins

    def configure_plugin_dlg(self, plugin_instance):
        """Produces a ConfigurePlugin dialog to configure the
        selected plugin"""
        cfg = None
        cfg_dlg = dialogs.ConfigurePluginDialog(self.view.parent, plugin_instance)
        if cfg_dlg.ShowModal() == wx.ID_OK:
            cfg = cfg_dlg.get_config()
        cfg_dlg.Destroy()
        return cfg

class PlotWindowController(BasicPlotWindowController):
    """Controller for PlotWindow class"""

    def __init__(self, view):
        self.view = view
        self.axes_grid = True
        self.model = model.PlotWindowModel(self)
        self.init_plot_defaults()
        self.available_plugins = self.generate_plugin_dict()

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
            # matplotlib forgets settings with replots -
            # save current values to reset after the replot
            titles = self.get_titles()
            if 2 in data.shape:
                self.view.axes.plot(data[0], data[1])
            elif data.ndim == 1:
                self.view.axes.plot(data)
            self.set_titles(plot=titles['plot'], x=titles['x'], y=titles['y'])
            self.view.axes.grid(self.axes_grid)

    @replace_plot
    def rectify_full(self):
        """Applies full rectification to the current data set"""
        self.model.rectify_full()

    def get_gates(self):
        """Returns a dict listing available window functions"""
        return self.model.gates

    def on_apply_gate(self, evt):
        """Handles request to apply window function ('gate' in UT)
        to data"""
        self.apply_gate(evt.GetId())

    @replace_plot
    def apply_gate(self, gate_id):
        """Applies a window function ('gate' in ultrasonics parlance)
        to the current data set"""
        if self.model.data is not None:
            rng_dlg = dialogs.FloatRangeDialog("Please specify the gate region.")
            if rng_dlg.ShowModal() == wx.ID_OK:
                try:
                    start_pos, end_pos = rng_dlg.GetValue()
                    self.model.apply_gate(gate_id, start_pos, end_pos)
                except ValueError as err: # negative dimensions
                    err_msg = "Unable to apply gate, error was:\n{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                        caption="Can't Apply Gate", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                finally:
                    rng_dlg.Destroy()

class ImgPlotWindowController(BasicPlotWindowController):
    """Controller for ImgPlotWindow class"""

    def __init__(self, view):
        self.view = view
        self.axes_grid = True
        self.model = model.ImgPlotWindowModel(self)
        self.colorbar = None
        self.init_plot_defaults()
        self.available_plugins = self.generate_plugin_dict()

    def init_plot_defaults(self):
        super(ImgPlotWindowController, self).init_plot_defaults()
        self.colormap = cm.get_cmap('Spectral')

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
            try:
                # matplotlib forgets settings with replots -
                # save current values to reapply after plot
                titles = self.get_titles()
                self.view.axes.cla()
                self.view.img = self.view.axes.imshow(data, cmap=self.colormap)
                if self.colorbar:
                    self.view.figure.delaxes(self.view.figure.axes[1])
                    self.view.figure.subplots_adjust(right=0.90)
                self.colorbar = self.view.figure.colorbar(self.view.img)
                self.set_titles(plot=titles['plot'], x=titles['x'], y=titles['y'])
                self.view.axes.grid(self.axes_grid)
            except TypeError as err: # Tried to imgplot 1D array
                err_msg = "Unable to plot data, error was:\n{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                    caption="Can't Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
                self.view.Destroy()

    def on_detrend_meanx(self, evt):
        """Applies constant (mean) detrend in X"""
        self.detrend(axis=0, type='constant')

    def on_detrend_meany(self, evt):
        """Applies constant (mean) detrend in Y"""
        self.detrend(axis=1, type='constant')

    def on_detrend_linearx(self, evt):
        """Applies linear detrend in X"""
        self.detrend(axis=0, type='linear')

    def on_detrend_lineary(self, evt):
        """Applies linear detrend in Y"""
        self.detrend(axis=1, type='linear')

    @replace_plot
    def detrend(self, axis, type):
        """Applies detrend along specified axis of specified type.
        Refreshes the plot."""
        self.model.detrend_data(axis, type)

    def on_set_cbarlbl(self, evt):
        """Sets the label for the imgplot's colorbar"""
        if self.colorbar is not None:
            label_dlg = wx.TextEntryDialog(parent=self.view.parent, message="Enter a new label for the colorbar",
                                           caption="Set Colorbar Label",
                                           defaultValue = self.get_titles()['colorbar'])
            if label_dlg.ShowModal() == wx.ID_OK:
                self.set_titles(colorbar=label_dlg.GetValue())

    def get_titles(self):
        """Returns the current titles for the plot, x & y axes, and colorbar as a dict
        with keys 'plot', 'x', 'y', 'colorbar'."""
        if self.colorbar is not None:
            # matplotlib has a set_label function but not a get - ??
            colorbar_lbl = self.colorbar._label
        else:
            colorbar_lbl = ''
        titles = {'plot':self.view.axes.get_title(),
                  'x':self.view.axes.get_xlabel(),
                  'y':self.view.axes.get_ylabel(),
                  'colorbar':colorbar_lbl}
        return titles

    def set_titles(self, plot=None, x=None, y=None, colorbar=None):
        """Sets one or more of plot, x/y axis, or colorbar labels to
        specified string.  If not specified, label is unchanged."""
        if plot:
            self.view.axes.set_title(plot)
        if x:
            self.view.axes.set_xlabel(x)
        if y:
            self.view.axes.set_ylabel(y)
        if colorbar:
            self.colorbar.set_label(colorbar)
        self.refresh_plot()

    def on_preview_cmaps(self, evt):
        """Generates a new dialog displaying all the built-in matplotlib
        colormaps and their reverse colormaps.  Original code courtesy
        SciPy Cookbook http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps"""
        wait_dlg = dialogs.progressDialog(dlg_title='Creating Colormap Preview',
                                          dlg_msg='Please wait, generating colormaps...')
        import matplotlib.pyplot as plt
        colormaps = self.model.get_colormap_choices()
        colormap_strip = self.model.generate_colormap_strip()
        num_maps = len(colormaps) + 1
        figure = plt.figure(figsize=(5, 8))
        figure.subplots_adjust(top=0.99, bottom=0.01, left=0.2, right=0.99)
        for i, m in enumerate(colormaps):
            ax = plt.subplot(num_maps, 1, i+1)
            plt.axis('off')
            plt.imshow(colormap_strip, aspect='auto', cmap=plt.get_cmap(m), origin='lower')
            pos = list(ax.get_position().bounds)
            figure.text(pos[0]-0.01, pos[1], m, fontsize=10, horizontalalignment='right')
        wait_dlg.close()
        plt.show()

    def on_select_cmap(self, evt):
        """Generates a list of available matplotlib colormaps and sets the plot's
        colormap to the user's choice."""
        colormaps = self.model.get_colormap_choices()
        cmap_dlg = wx.lib.dialogs.singleChoiceDialog(self.view.parent, "Select Colormap",
                                                     "Please select a colormap for this plot.",
                                                     colormaps)
        if cmap_dlg.accepted is True:
            colormap = cmap_dlg.selection
            if colormap == '':
                self.colormap = cm.spectral
            else:
                self.colormap = cm.get_cmap(colormap)
            if self.view.img != None:
                self.view.img.set_cmap(self.colormap)
                self.refresh_plot()