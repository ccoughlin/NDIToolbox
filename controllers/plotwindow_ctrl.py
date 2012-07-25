"""plotwindow_ctrl.py - defines the controller for plotwindow.py

Chris R. Coughlin (TRI/Austin, Inc.)
"""
__author__ = 'Chris R. Coughlin'

from views import dialogs
from views import fetchplugin_dialog
from models import mainmodel
from models import ndescanhandler
import models.plotwindow_model as model
import matplotlib
import matplotlib.axes
from matplotlib import cm
import wx
import wx.lib.dialogs
from functools import wraps
import multiprocessing
import os.path
import Queue

def replace_plot(fn):
    """Decorator function - runs the specified function and updates the plot.
    Designed to work with PlotWindowController instances.
    """

    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        if self.model.data is not None:
            if isinstance(self.view.axes, matplotlib.axes.Subplot):
                self.view.axes.hold()
            else:
                for ax in self.view.axes:
                    ax.hold()
            fn(self, *args, **kwargs)
            self.plot(self.model.data)
            self.refresh_plot()

            if isinstance(self.view.axes, matplotlib.axes.Subplot):
                self.view.axes.hold()
            else:
                for ax in self.view.axes:
                    ax.hold()

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

    def __init__(self, view, data_file):
        self.view = view
        self.axes_grid = True
        self.model = model.BasicPlotWindowModel(self, data_file)
        self.init_plot_defaults()

    @property
    def available_plugins(self):
        """Returns a list of available plugins suitable for
        inclusion in a wxMenu"""
        return self.generate_plugin_dict()

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

    def on_install_plugin(self, evt):
        """Handles request to install a local plugin"""
        file_dlg = wx.FileDialog(parent=self.view,
                                 message="Please select a plugin archive to install.",
                                 wildcard="ZIP files (*.zip)|*.zip|All files (*.*)|*.*")
        if file_dlg.ShowModal() == wx.ID_OK:
            dlg = fetchplugin_dialog.FetchPluginDialog(parent=self.view,
                                                       plugin_path=file_dlg.GetPath())
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    dlg.install_plugin()
                    self.view.init_plugins_menu()
                except Exception as err:
                    err_msg = "{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Install Plugin",
                                               style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
            dlg.Destroy()
        file_dlg.Destroy()

    def on_download_plugin(self, evt):
        """Handles request to download and install a plugin"""
        dlg = fetchplugin_dialog.FetchRemotePluginDialog(parent=self.view)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                dlg.install_plugin()
                self.view.init_plugins_menu()
            except Exception as err:
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Install Plugin", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
        dlg.Destroy()

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
                plugin_class, check_plugin_config_instance = self.model.get_plugin(plugin[0])
                if hasattr(check_plugin_config_instance, "config"):
                    cfg = self.configure_plugin_dlg(check_plugin_config_instance)
                    if cfg is None:
                        return
                plugin_queue = multiprocessing.Queue()
                plugin_process = multiprocessing.Process(target=plugin_wrapper,
                                                         args=(plugin_class, self.data, plugin_queue, cfg))
                plugin_process.daemon = True
                plugin_process.start()
                keepGoing = True
                # TODO: move progress dialog to dialogs module
                try:
                    progress_dlg = wx.ProgressDialog("Running Plugin",
                                                     "Please wait, executing plugin...",
                                                     parent=self.view,
                                                     style=wx.PD_CAN_ABORT)
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
                        wx.getApp().Yield()
                finally:
                    progress_dlg.Destroy()

    def on_close(self, evt):
        """Handles request to close plot window"""
        self.view.Destroy()

    def on_save_data(self, evt):
        """Handles request to save current data set to disk"""
        default_path, default_file = os.path.split(self.model.data_file)
        wild_card = "NDIToolbox data files (*.hdf5)|*.hdf5|All files (*.*)|*.*"
        save_dlg = wx.FileDialog(self.view, message="Save File As...",
                                 defaultDir=default_path,
                                 defaultFile=default_file,
                                 wildcard=wild_card,
                                 style=wx.SAVE | wx.OVERWRITE_PROMPT)
        if save_dlg.ShowModal() == wx.ID_OK:
            mainmodel.save_data(save_dlg.GetPath(), self.data)
            self.view.parent.refresh()
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
        label_dlg = wx.TextEntryDialog(parent=self.view.parent,
                                       message="Enter a new label for the X-Axis",
                                       caption="Set X Axis Label",
                                       defaultValue=self.get_titles()['x'])
        if label_dlg.ShowModal() == wx.ID_OK:
            self.set_titles(x=label_dlg.GetValue())

    def on_set_ylabel(self, evt):
        """Handles the set y-axis label event"""
        label_dlg = wx.TextEntryDialog(parent=self.view.parent,
                                       message="Enter a new label for the Y-Axis",
                                       caption="Set Y Axis Label",
                                       defaultValue=self.get_titles()['y'])
        if label_dlg.ShowModal() == wx.ID_OK:
            self.set_titles(y=label_dlg.GetValue())

    def on_set_plottitle(self, evt):
        """Handles the set x-axis label event"""
        label_dlg = wx.TextEntryDialog(parent=self.view.parent,
                                       message="Enter a new title for the plot",
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

    @replace_plot
    def revert(self):
        """Reverts data to original"""
        self.model.revert_data()

    def load_data(self):
        """Loads the data from the specified file name"""
        self.model.load_data()

    def get_plugins(self):
        """Returns a list of the available NDIToolbox plugins"""
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

    def __init__(self, view, data_file):
        self.view = view
        self.axes_grid = True
        self.model = model.PlotWindowModel(self, data_file)
        self.init_plot_defaults()

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
            try:
                # matplotlib forgets settings with replots -
                # save current values to reset after the replot
                titles = self.get_titles()
                if 2 in data.shape: # Assume data is X, Y
                    self.view.axes.plot(data[0], data[1])
                elif data.ndim == 1:
                    self.view.axes.plot(data)
                elif data.ndim == 3:
                    # 3D data; offer to take a slice in X, Y, or Z to plot
                    slice_dlg = dialogs.LinearSliceDialog(parent=self.view, data=data,
                                                          title="Select Axis To Plot")
                    if slice_dlg.ShowModal() == wx.ID_OK:
                        data = slice_dlg.get_data_slice()
                        self.plot(data)
                    slice_dlg.Destroy()
                self.set_titles(plot=titles['plot'], x=titles['x'], y=titles['y'])
                self.view.axes.grid(self.axes_grid)
            except OverflowError as err: # Data too large to plot
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()

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
                    err_msg = "{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Apply Gate", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                finally:
                    rng_dlg.Destroy()

    def on_rectify(self, evt):
        """Handles request to apply rectification"""
        self.rectify_full()


class BasicImgPlotWindowController(BasicPlotWindowController):
    """Base class for ImgPlotWindow Controllers"""

    def __init__(self, view, data_file):
        self.view = view
        self.axes_grid = True
        self.model = model.ImgPlotWindowModel(self, data_file)
        self.colorbar = None
        self.init_plot_defaults()

    def init_plot_defaults(self):
        super(BasicImgPlotWindowController, self).init_plot_defaults()
        self.colormap = cm.get_cmap('Spectral')

    def on_set_cbarlbl(self, evt):
        """Sets the label for the imgplot's colorbar"""
        if self.colorbar is not None:
            label_dlg = wx.TextEntryDialog(parent=self.view.parent,
                                           message="Enter a new label for the colorbar",
                                           caption="Set Colorbar Label",
                                           defaultValue=self.get_titles()['colorbar'])
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
        titles = {'plot': self.view.axes.get_title(),
                  'x': self.view.axes.get_xlabel(),
                  'y': self.view.axes.get_ylabel(),
                  'colorbar': colorbar_lbl}
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
        wx.BeginBusyCursor()
        import matplotlib.pyplot as plt

        colormaps = self.model.get_colormap_choices()
        colormap_strip = self.model.generate_colormap_strip()
        num_maps = len(colormaps) + 1
        figure = plt.figure(figsize=(5, 8))
        figure.subplots_adjust(top=0.99, bottom=0.01, left=0.2, right=0.99)
        for i, m in enumerate(colormaps):
            if not m.endswith("_r"):
                ax = plt.subplot(num_maps, 1, i + 1)
                plt.axis('off')
                plt.imshow(colormap_strip, aspect='equal', cmap=plt.get_cmap(m), origin='lower')
                pos = list(ax.get_position().bounds)
                figure.text(pos[0] - 0.01, pos[1], m, fontsize=10, horizontalalignment='right')
        plt.show()
        wx.EndBusyCursor()

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
            if self.view.img is not None:
                self.view.img.set_cmap(self.colormap)
                self.refresh_plot()


class ImgPlotWindowController(BasicImgPlotWindowController):
    """Controller for ImgPlotWindow class"""

    def __init__(self, view, data_file):
        super(ImgPlotWindowController, self).__init__(view, data_file)

    def check_data_dims(self):
        """If the data is a 3D array, set the data to a single 2D
        slice."""
        if self.data.ndim == 3:
            slice_dlg = dialogs.PlanarSliceDialog(parent=self.view, data=self.data,
                                                  title="Specify 2D Plane")
            if slice_dlg.ShowModal() == wx.ID_OK:
                self.model.data = slice_dlg.get_data_slice()
                self.model.original_data = self.model.data
            slice_dlg.Destroy()

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
            try:
                # matplotlib forgets settings with replots -
                # save current values to reapply after plot
                titles = self.get_titles()
                self.view.axes.cla()
                self.view.img = self.view.axes.imshow(data, aspect="equal", origin="lower", cmap=self.colormap)
                if self.colorbar:
                    self.view.figure.delaxes(self.view.figure.axes[1])
                    self.view.figure.subplots_adjust(right=0.90)
                self.colorbar = self.view.figure.colorbar(self.view.img)
                self.set_titles(plot=titles['plot'], x=titles['x'], y=titles['y'])
                self.view.axes.grid(self.axes_grid)
            except TypeError as err: # Tried to imgplot 1D array
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
            except OverflowError as err: # Data too large to plot
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()

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

    @replace_plot
    def on_flipud(self, evt):
        """Handles request to flip the data vertically"""
        self.model.flipud_data()

    @replace_plot
    def on_fliplr(self, evt):
        """Handles request to flip the data horizontally"""
        self.model.fliplr_data()

    @replace_plot
    def on_rot90ccw(self, evt):
        """Handles request to rotate data 90 degrees counterclockwise"""
        self.model.rotate_data(1)

    @replace_plot
    def on_rot90cw(self, evt):
        """Handles request to rotate data 90 degrees clockwise"""
        self.model.rotate_data(3)

    @replace_plot
    def on_rot180(self, evt):
        """Handles request to rotate data 180 degrees"""
        self.model.rotate_data(2)

    @replace_plot
    def on_transpose(self, evt):
        """Handles request to transpose data"""
        self.model.transpose_data()


class MegaPlotWindowController(BasicImgPlotWindowController):
    """Controller for MegaPlotWindows"""

    def __init__(self, view, data_file):
        self.view = view
        self.slice_idx = 0
        self.axes_grid = True
        self.model = model.MegaPlotWindowModel(self, data_file)
        self.colorbar = None
        self.init_plot_defaults()

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
            self.scnr = ndescanhandler.NDEScanHandler(self.data)
            try:
                if self.view.slice_cb.IsChecked():
                    self.plot_cscan(self.scnr.cscan_data(self.slice_idx), self.slice_idx)
            except TypeError as err: # Tried to imgplot 1D array
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
            except OverflowError as err: # Data too large to plot
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()

    def plot_ascan(self, ascan_data, xpos, ypos):
        """Plots the provided A-scan data"""
        self.view.ascan_axes.cla()
        self.view.ascan_plt = self.view.ascan_axes.plot(ascan_data)
        self.view.ascan_axes.autoscale_view(tight=True)
        self.view.ascan_axes.set_title("A Scan x={0} y={1}".format(xpos, ypos))

    def plot_hbscan(self, hbscan_data, ypos, slice_idx):
        """Plots the provided horizontal B-scan data"""
        self.view.hbscan_axes.cla()
        self.view.hbscan_plt = self.view.hbscan_axes.plot(hbscan_data)
        self.view.hbscan_axes.autoscale_view(tight=True)
        self.view.hbscan_axes.set_title("Horizontal B Scan y={0} z={1}".format(ypos, slice_idx))

    def plot_vbscan(self, vbscan_data, xpos, slice_idx):
        """Plots the provided vertical B-scan data"""
        self.view.vbscan_axes.cla()
        self.view.vbscan_plt = self.view.vbscan_axes.plot(vbscan_data)
        self.view.vbscan_axes.autoscale_view(tight=True)
        self.view.vbscan_axes.set_title("Vertical B Scan x={0} z={1}".format(xpos, slice_idx))

    def plot_cscan(self, cscan_data, slice_idx):
        """Plots the supplied C-scan data"""
        self.view.cscan_axes.cla()
        self.view.cscan_img = self.view.cscan_axes.imshow(cscan_data, aspect='auto',
                                                          origin='lower', cmap=self.colormap,
                                                          interpolation='nearest')
        self.view.cscan_axes.set_title("C Scan z={0}".format(slice_idx))

    def get_plot_choice(self):
        """Presents single choice dialog to the user to select an Axes to modify."""
        plot_choices = ["A-Scan", "Horizontal B-Scan", "Vertical B-Scan", "C-Scan"]
        choice_dlg = wx.SingleChoiceDialog(parent=self.view, message="Please select a plot to modify.",
                                           caption="Available Plots", choices=plot_choices)
        if choice_dlg.ShowModal() == wx.ID_OK:
            return self.view.axes[choice_dlg.GetSelection()]
        choice_dlg.Destroy()
        return None

    def on_set_xlabel(self, evt):
        """Handles the set x-axis label event"""
        axis = self.get_plot_choice()
        if axis is not None:
            label_dlg = wx.TextEntryDialog(parent=self.view.parent,
                                           message="Enter a new label for the X-Axis",
                                           caption="Set X Axis Label",
                                           defaultValue=self.get_titles(axis)['x'])
            if label_dlg.ShowModal() == wx.ID_OK:
                self.set_titles(axis, x=label_dlg.GetValue())
            label_dlg.Destroy()

    def on_set_ylabel(self, evt):
        """Handles the set y-axis label event"""
        axis = self.get_plot_choice()
        if axis is not None:
            label_dlg = wx.TextEntryDialog(parent=self.view.parent,
                                           message="Enter a new label for the Y-Axis",
                                           caption="Set Y Axis Label",
                                           defaultValue=self.get_titles(axis)['y'])
            if label_dlg.ShowModal() == wx.ID_OK:
                self.set_titles(axis, y=label_dlg.GetValue())
            label_dlg.Destroy()

    def on_set_plottitle(self, evt):
        """Handles the set x-axis label event"""
        axis = self.get_plot_choice()
        if axis is not None:
            label_dlg = wx.TextEntryDialog(parent=self.view.parent,
                                           message="Enter a new title for the plot",
                                           caption="Set Plot Title",
                                           defaultValue=self.get_titles(axis)['plot'])
            if label_dlg.ShowModal() == wx.ID_OK:
                self.set_titles(axis, plot=label_dlg.GetValue())
            label_dlg.Destroy()

    def get_titles(self, axes_inst):
        """Returns the current titles for the specified AxesSubplot instance's
        plot, x and y axes as a dict with keys 'plot', 'x', 'y'."""
        if isinstance(axes_inst, matplotlib.axes.Subplot):
            titles = {'plot': axes_inst.get_title(),
                      'x': axes_inst.get_xlabel(),
                      'y': axes_inst.get_ylabel()}
            return titles
        return None

    def set_titles(self, axes_inst, plot=None, x=None, y=None):
        """Sets one or more of plot, x, or y axis titles to specified
        string for the specified AxesSubplot instance.
        If not specified, title is left unchanged."""
        if isinstance(axes_inst, matplotlib.axes.Subplot):
            if plot:
                axes_inst.set_title(plot)
            if x:
                axes_inst.set_xlabel(x)
            if y:
                axes_inst.set_ylabel(y)
            self.refresh_plot()

    def on_click(self, evt):
        """Handles mouse click in the C Scan - update other plots"""
        if not self.view.navtools_cb.IsChecked():
            if evt.inaxes == self.view.cscan_axes:
                xpos = int(evt.xdata)
                ypos = int(evt.ydata)
                self.update_plot(xpos, ypos)

    def on_check_navtools(self, evt):
        """Handles toggle of enable/disable navigation toolbar checkbox"""
        self.view.toggle_toolbar()

    def on_sliceidx_change(self, evt):
        """Responds to changes in the z position spin control"""
        self.update_plot(self.view.xpos_sc.GetValue(), self.view.ypos_sc.GetValue(),
                         self.view.slice_sc.GetValue())

    def on_xy_change(self, evt):
        """Responds to changes in the x position and y position spin controls"""
        self.update_plot(self.view.xpos_sc.GetValue(), self.view.ypos_sc.GetValue())

    @replace_plot
    def update_plot(self, xpos, ypos, slice_idx=None):
        """Updates the A and B scans based on the provided
        (x,y) position in the data.  If slice_idx is provided
        the C scan plot is updated to that position, default
        is to leave unchanged if slice_idx is None."""
        self.view.xpos_sc.SetValue(xpos)
        self.view.ypos_sc.SetValue(ypos)
        self.plot_ascan(self.scnr.ascan_data(xpos, ypos), xpos, ypos)
        self.plot_hbscan(self.view.cscan_img.get_array()[ypos, :], slice_idx=self.slice_idx, ypos=ypos)
        self.plot_vbscan(self.view.cscan_img.get_array()[:, xpos], slice_idx=self.slice_idx, xpos=xpos)
        if slice_idx is not None:
            self.slice_idx = slice_idx
            if self.view.slice_cb.IsChecked():
                self.plot_cscan(self.scnr.cscan_data(self.slice_idx), self.slice_idx)
        self.refresh_plot()

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
            if self.view.cscan_img is not None:
                self.view.cscan_img.set_cmap(self.colormap)
                self.refresh_plot()

    @replace_plot
    def on_toggle_grid(self, evt):
        """Toggles the plot's grid on or off"""
        for ax in self.view.axes:
            ax.grid()
        self.axes_grid = not self.axes_grid
        self.refresh_plot()

    @replace_plot
    def on_rectify(self, evt):
        """Handles request to apply rectification to A-scan plot"""
        xpos = self.view.xpos_sc.GetValue()
        ypos = self.view.ypos_sc.GetValue()
        self.plot_ascan(self.model.rectify_full(self.scnr.ascan_data(xpos, ypos)), xpos, ypos)

    def get_gates(self):
        """Returns a dict listing available window functions"""
        return self.model.gates

    @replace_plot
    def on_apply_gate(self, evt):
        """Handles request to apply window function ('gate' in UT)
        to A-scan"""
        self.apply_gate(evt.GetId())

    def apply_gate(self, gate_id):
        if self.model.data is not None:
            rng_dlg = dialogs.FloatRangeDialog("Please specify the gate region.")
            if rng_dlg.ShowModal() == wx.ID_OK:
                try:
                    start_pos, end_pos = rng_dlg.GetValue()
                    xpos = self.view.xpos_sc.GetValue()
                    ypos = self.view.ypos_sc.GetValue()
                    ascan_data = self.scnr.ascan_data(xpos, ypos)
                    self.plot_ascan(self.model.apply_gate(ascan_data, gate_id, start_pos, end_pos), xpos, ypos)
                except ValueError as err: # negative dimensions
                    err_msg = "{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Apply Gate", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                finally:
                    rng_dlg.Destroy()

    def on_define_cscan(self, evt):
        """Handles request to define the data used
        to produce the C Scan imgplot"""
        self.view.slice_cb.SetValue(False)
        self.define_cscan()

    @replace_plot
    def define_cscan(self):
        """Specify a range of data and a function
        to generate a C Scan plot"""
        if self.model.data is not None:
            rng_dlg = dialogs.FloatRangeDialog("Please specify the index range in Z.")
            if rng_dlg.ShowModal() == wx.ID_OK:
                try:
                    start_pos, end_pos = rng_dlg.GetValue()
                    fn_dlg = wx.SingleChoiceDialog(parent=self.view, caption="Choose C Scan Function",
                                                   message="Please choose a function to generate the C Scan data.",
                                                   choices=self.scnr.available_cscan_function_names)
                    if fn_dlg.ShowModal() == wx.ID_OK:
                        wx.BeginBusyCursor()
                        cscan_data = self.scnr.gen_cscan(start_pos, end_pos,
                                                         fn=self.scnr.available_cscan_functions[fn_dlg.GetSelection()])
                        self.plot_cscan(cscan_data, self.slice_idx)
                        plot_title = "C Scan {0} z={1}:{2}".format(
                            self.scnr.available_cscan_function_names[fn_dlg.GetSelection()], start_pos, end_pos)
                        self.set_titles(self.view.cscan_axes, plot=plot_title)
                        wx.EndBusyCursor()
                except ValueError as err:
                    err_msg = "{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Generate C Scan", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                finally:
                    rng_dlg.Destroy()