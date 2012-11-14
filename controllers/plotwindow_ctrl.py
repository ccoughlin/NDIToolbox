"""plotwindow_ctrl.py - defines the controller for plotwindow.py

Chris R. Coughlin (TRI/Austin, Inc.)
"""
__author__ = 'Chris R. Coughlin'

from views import dialogs
from views import fetchplugin_dialog
from views import colormapcreator
from models import mainmodel
from models import dataio
from models import ndescanhandler
import models.plotwindow_model as model
import matplotlib
import matplotlib.axes
import wx
import wx.lib.dialogs
from functools import wraps
import os.path
import Queue

module_logger = mainmodel.get_logger(__name__)

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


class BasicPlotWindowController(object):
    """Base class for PlotWindows"""

    def __init__(self, view, data_file):
        self.view = view
        self.axes_grid = True
        self.model = model.BasicPlotWindowModel(self, data_file)
        self.init_plot_defaults()
        module_logger.info("Successfully initialized BasicPlotWindowController.")

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
                    module_logger.error("Unable to install plugin: {0}".format(err))
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
                module_logger.error("Unable to install plugin: {0}".format(err))
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Install Plugin", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
        dlg.Destroy()

    def on_run_toolkit(self, evt):
        """Handles request to run a plugin"""
        self.run_toolkit(evt.GetId())

    @replace_plot
    def run_toolkit(self, requested_toolkit_id):
        """Runs toolkit with specified ID on current data set,
        replaces current data and refreshes plot"""
        for toolkit_id, toolkit in self.available_plugins.items():
            if requested_toolkit_id == toolkit_id:
                plugin_class = self.model.get_plugin(toolkit[0])
                module_logger.info("Attempt to run plugin {0}".format(plugin_class))
                self.run_plugin(plugin_class)

    @replace_plot
    def run_plugin(self, plugin_cls, **kwargs):
        """Runs plugin of specified class plugin_cls on current data set,
        replaces current data and refreshes plot"""
        cfg = None
        # Instantiate the plugin to see if it has a self.config dict
        # that should be configured by the user prior to execution
        plugin_instance = plugin_cls()
        if hasattr(plugin_instance, "config"):
            cfg = self.configure_plugin_dlg(plugin_instance)
            if cfg is None:
                return
        try:
            plugin_process, plugin_queue, exception_queue = mainmodel.run_plugin(plugin_cls, self.data, cfg, **kwargs)
        except MemoryError as err: # Insufficient memory to run plugin with current data
            err_dlg = wx.MessageDialog(self.view, message="Insufficient memory to run plugin.",
                                       caption="Unable To Run Plugin",
                                       style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()
            return
        keepGoing = True
        try:
            progress_dlg = wx.ProgressDialog("Running Plugin",
                                             "Please wait, executing plugin...",
                                             parent=self.view,
                                             style=wx.PD_CAN_ABORT)
            while keepGoing:
                wx.MilliSleep(125)
                (keepGoing, skip) = progress_dlg.UpdatePulse()
                try:
                    exc_type, exc = exception_queue.get(block=False)
                    module_logger.error("Error occurred running plugin: {0}".format(exc))
                    err_msg = "An error occurred while running the plugin:\n{0}".format(exc)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Run Plugin",
                                               style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    break
                except Queue.Empty:
                    pass
                try:
                    returned_data = plugin_queue.get(False)
                except Queue.Empty:
                    continue
                if returned_data is not None:
                    self.model.data = returned_data
                    break
                if not keepGoing:
                    break
                wx.getApp().Yield()
        finally:
            plugin_process.join()
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
            dataio.save_data(save_dlg.GetPath(), self.data)
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
        try:
            self.model.load_data()
        except MemoryError as err: # out of memory
            module_logger.exception("Insufficient memory - {0}".format(err))
            raise MemoryError("Insufficient memory to load data")

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
        self.gates = {}
        self.get_gates()
        self.init_plot_defaults()
        module_logger.info("PlotWindowController successfully initialized.")

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
            try:
                # matplotlib forgets settings with replots -
                # save current values to reset after the replot
                titles = self.get_titles()
                if data.ndim == 1:
                    self.view.axes.plot(data)
                elif data.ndim == 2:
                    if 2 in data.shape: # Assume data is X, Y
                        self.view.axes.plot(data[0], data[1])
                    else:
                        slice_dlg = dialogs.LinearSliceDialog(parent=self.view, data_shape=data.shape,
                                                              title="Select Axis To Plot")
                        if slice_dlg.ShowModal() == wx.ID_OK:
                            self.model.load_data(slice_idx=slice_dlg.get_data_slice())
                            self.plot(self.data)
                        slice_dlg.Destroy()
                elif data.ndim == 3:
                    # 3D data; offer to take a slice in X, Y, or Z to plot
                    slice_dlg = dialogs.LinearSliceDialog(parent=self.view, data_shape=data.shape,
                                                          title="Select Axis To Plot")
                    if slice_dlg.ShowModal() == wx.ID_OK:
                        self.model.load_data(slice_idx=slice_dlg.get_data_slice())
                        self.plot(self.data)
                    slice_dlg.Destroy()
                self.set_titles(plot=titles['plot'], x=titles['x'], y=titles['y'])
                self.view.axes.grid(self.axes_grid)
            except OverflowError as err: # Data too large to plot
                module_logger.error("Data too large to plot: {0}".format(OverflowError))
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()

    @replace_plot
    def rectify_full(self):
        """Applies full rectification to the current data set"""
        self.model.rectify_full()

    def generate_gate_id(self):
        """Generates an ID number for the specified gate name.
        Used to identify gates in wxPython menu events."""
        id = 1011 + len(self.gates)
        return id

    def get_gates(self):
        """Returns a dict listing available window functions"""
        for gate_name in self.model.gates:
            self.gates[self.generate_gate_id()] = gate_name

    def on_apply_gate(self, evt):
        """Handles request to apply window function ('gate' in UT)
        to data"""
        self.run_gate(evt.GetId())

    @replace_plot
    def run_gate(self, gate_id):
        """Runs toolkit with specified ID on current data set,
        replaces current data and refreshes plot"""
        if self.model.data is not None:
            rng_dlg = dialogs.FloatRangeDialog("Please specify the gate region.")
            if rng_dlg.ShowModal() == wx.ID_OK:
                try:
                    start_pos, end_pos = rng_dlg.GetValue()
                    gate_name, gate_cls = self.gates.get(gate_id)
                    self.run_plugin(gate_cls, start_pos=start_pos, end_pos=end_pos)
                except ValueError as err: # negative dimensions
                    module_logger.error("Unable to apply gate, user provided negative dimensions: {0}, {1}".format(
                        start_pos, end_pos
                    ))
                    err_msg = "{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Apply Gate", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                except IndexError: # specified nonexistent gate id
                    module_logger.error("Unable to apply gate, couldn't find specified gate function.")
                    err_msg = "Unable to locate specified gate function."
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
        module_logger.info("Successfully initialized BasicImgPlotWindowController.")

    def init_plot_defaults(self):
        super(BasicImgPlotWindowController, self).init_plot_defaults()
        cfg = mainmodel.get_config()
        if cfg.has_option("ImgPlot", "colormap"):
            self.colormap = self.model.get_cmap(cfg.get("ImgPlot", "colormap"))
        else:
            self.colormap = self.model.get_cmap('Spectral')

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
                plt.imshow(colormap_strip, aspect='equal', cmap=self.model.get_cmap(m), origin='lower')
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
            cfg = mainmodel.get_config()
            colormap = cmap_dlg.selection
            if colormap == '':
                self.colormap = self.model.get_cmap('Spectral')
                cfg.set("ImgPlot", {"colormap":"spectral"})
            else:
                self.colormap = self.model.get_cmap(colormap)
                cfg.set("ImgPlot", {"colormap":colormap})
            if self.view.img is not None:
                self.view.img.set_cmap(self.colormap)
                self.refresh_plot()

    def on_create_cmap(self, evt):
        """Handles request to create a new matplotlib colormap"""
        cmapcreator_ui = colormapcreator.ColormapCreatorUI(parent=self.view)
        cmapcreator_ui.Show()

class ImgPlotWindowController(BasicImgPlotWindowController):
    """Controller for ImgPlotWindow class"""

    def __init__(self, view, data_file):
        super(ImgPlotWindowController, self).__init__(view, data_file)
        module_logger.info("Successfully initialized ImgPlotWindowController.")

    def check_data_dims(self):
        """If the data is a 3D array, set the data to a single 2D
        slice."""
        if self.data is None:
            self.load_data()
        if self.data.ndim == 3:
            slice_dlg = dialogs.PlanarSliceDialog(parent=self.view, data_shape=self.data.shape,
                                                  title="Specify 2D Plane")
            if slice_dlg.ShowModal() == wx.ID_OK:
                self.model.load_data(slice_idx=slice_dlg.get_data_slice())
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
                module_logger.error("Unable to plot data, user attempted to imgplot 1D array: {0}".format(err))
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
            except OverflowError as err: # Data too large to plot
                module_logger.error("Unable to plot data, data too large: {0}".format(err))
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


class MegaPlotWindowController(BasicImgPlotWindowController, PlotWindowController):
    """Controller for MegaPlotWindows"""

    def __init__(self, view, data_file):
        self.view = view
        self.slice_idx = 0
        self.xpos = 0
        self.ypos = 0
        self.axes_grid = True
        self.model = model.MegaPlotWindowModel(self, data_file)
        self.colorbar = None
        self.gate_coords = [None, None]
        self.gates = {}
        self.get_gates()
        self.init_plot_defaults()
        module_logger.info("Successfully initialized MegaPlotWindowController.")

    def init_plot_defaults(self):
        """Initializes the defaults for the Megaplot presentation."""
        super(MegaPlotWindowController, self).init_plot_defaults()
        cfg = mainmodel.get_config()
        if cfg.has_option("MegaPlot", "conventional bscans"):
            self.conventional_bscans = cfg.get_boolean("MegaPlot", "conventional bscans")
        else:
            self.conventional_bscans = False

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
            self.scnr = ndescanhandler.NDEScanHandler(self.data)
            try:
                if self.view.slice_cb.IsChecked():
                    self.plot_cscan(self.scnr.cscan_data(self.slice_idx), self.slice_idx)
            except TypeError as err: # Tried to imgplot 1D array
                module_logger.error("Unable to plot data, user attempted to imgplot 1D array: {0}".format(err))
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Plot Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
            except OverflowError as err: # Data too large to plot
                module_logger.error("Unable to plot data, data too large to plot: {0}".format(err))
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

    def plot_hbscan(self, hbscan_data, ypos, slice_idx=None):
        """Plots the provided horizontal B-scan data.  If plotting a conventional Bscan, the slice_idx parameter
        can be omitted."""
        self.view.hbscan_axes.cla()
        if hbscan_data.ndim == 1:
            self.view.hbscan_plt = self.view.hbscan_axes.plot(hbscan_data)
            self.view.hbscan_axes.set_title("Horizontal B Scan y={0} z={1}".format(ypos, slice_idx))
        else:
            self.view.hbscan_plt = self.view.hbscan_axes.imshow(hbscan_data, aspect='auto',
                                                                origin='lower', cmap=self.colormap,
                                                                interpolation='nearest')
            self.view.hbscan_axes.set_title("Horizontal B Scan y={0}".format(ypos))
        self.view.hbscan_axes.autoscale_view(tight=True)


    def plot_vbscan(self, vbscan_data, xpos, slice_idx=None):
        """Plots the provided vertical B-scan data.  If plotting a conventional Bscan, the slice_idx parameter
        can be omitted."""
        self.view.vbscan_axes.cla()
        if vbscan_data.ndim == 1:
            self.view.vbscan_plt = self.view.vbscan_axes.plot(vbscan_data)
            self.view.vbscan_axes.set_title("Vertical B Scan x={0} z={1}".format(xpos, slice_idx))
        else:
            self.view.vbscan_plt = self.view.vbscan_axes.imshow(vbscan_data, aspect='auto',
                                                                origin='lower', cmap=self.colormap,
                                                                interpolation='nearest')
            self.view.vbscan_axes.set_title("Vertical B Scan x={0}".format(xpos))
        self.view.vbscan_axes.autoscale_view(tight=True)

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
        if not self.view.navtools_enabled():
            if evt.inaxes == self.view.cscan_axes:
                xpos = int(evt.xdata)
                ypos = int(evt.ydata)
                self.update_plot(xpos, ypos)
            if evt.inaxes == self.view.ascan_axes:
                xpos = int(evt.xdata)
                if self.gate_coords[0] is None:
                    self.gate_coords[0] = xpos
                    self.view.ascan_axes.axvline(x=xpos, color='r', linestyle='--')
                elif self.gate_coords[1] is None:
                    self.gate_coords[1] = xpos
                    self.view.ascan_axes.axvline(x=xpos, color='r', linestyle='--')
                    self.gate_coords.sort()
                else:
                    self.gate_coords[0] = None
                    self.gate_coords[1] = None
                    while len(self.view.ascan_axes.lines) > 1:
                        self.view.ascan_axes.lines.pop(-1)
                self.view.canvas.draw()


    def on_check_navtools(self, evt):
        """Handles toggle of enable/disable navigation toolbar checkbox"""
        self.view.toggle_toolbar()

    def set_navtools_config(self, navtools_enabled):
        """Sets the enable navtools option in the config"""
        cfg = mainmodel.get_config()
        cfg.set("MegaPlot", {"enable navtools":navtools_enabled})

    def get_navtools_config(self):
        """Returns the enable navtools setting from config."""
        cfg = mainmodel.get_config()
        if cfg.has_option("MegaPlot", "enable navtools"):
            return cfg.get_boolean("MegaPlot", "enable navtools")
        return True

    def on_sliceidx_change(self, evt):
        """Responds to changes in the z position spin control"""
        self.update_plot(self.view.xpos_sc.GetValue(), self.view.ypos_sc.GetValue(),
                         self.view.slice_sc.GetValue())

    def on_xy_change(self, evt):
        """Responds to changes in the x position and y position spin controls"""
        self.update_plot(self.view.xpos_sc.GetValue(), self.view.ypos_sc.GetValue())

    @replace_plot
    def update_plot(self, xpos=None, ypos=None, slice_idx=None):
        """Updates the A and B scans based on the provided (x,y) position in the data.  If xpos and/or ypos
        are None (default), A and B scans are updated on the last (x,y) position selected by the user.
        If slice_idx is provided the C scan plot is updated to that position, default is to leave unchanged if
        slice_idx is None."""
        if xpos is None:
            xpos = self.xpos
        else:
            self.xpos = xpos
        if ypos is None:
            ypos = self.ypos
        else:
            self.ypos = ypos
        self.view.xpos_sc.SetValue(xpos)
        self.view.ypos_sc.SetValue(ypos)
        self.plot_ascan(self.scnr.ascan_data(xpos, ypos), xpos, ypos)
        if self.conventional_bscans is False:
            self.plot_hbscan(self.view.cscan_img.get_array()[ypos, :], slice_idx=self.slice_idx, ypos=ypos)
            self.plot_vbscan(self.view.cscan_img.get_array()[:, xpos], slice_idx=self.slice_idx, xpos=xpos)
        else:
            self.plot_hbscan(self.scnr.hbscan_data(ypos), ypos)
            self.plot_vbscan(self.scnr.vbscan_data(xpos), xpos)
        if slice_idx is not None:
            self.slice_idx = slice_idx
            if self.view.slice_cb.IsChecked():
                self.plot_cscan(self.scnr.cscan_data(self.slice_idx), self.slice_idx)
        if self.gate_coords != [None, None]:
            self.view.ascan_axes.axvline(x=self.gate_coords[0], color='r', linestyle='--')
            self.view.ascan_axes.axvline(x=self.gate_coords[1], color='r', linestyle='--')
        self.refresh_plot()

    def on_select_cmap(self, evt):
        """Generates a list of available matplotlib colormaps and sets the plot's
        colormap to the user's choice."""
        colormaps = self.model.get_colormap_choices()
        cmap_dlg = wx.lib.dialogs.singleChoiceDialog(self.view.parent, "Select Colormap",
                                                     "Please select a colormap for this plot.",
                                                     colormaps)
        if cmap_dlg.accepted is True:
            cfg = mainmodel.get_config()
            colormap = cmap_dlg.selection
            if colormap == '':
                self.colormap = self.model.get_cmap('Spectral')
                cfg.set("ImgPlot", {"colormap":"spectral"})
            else:
                self.colormap = self.model.get_cmap(colormap)
                cfg.set("ImgPlot", {"colormap":colormap})
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
    def on_change_bscans(self, evt):
        """Toggles using conventional Bscan imgplots or 1D cross-sections through the current Cscan"""
        self.conventional_bscans = self.view.plot_conventional_bscans
        cfg = mainmodel.get_config()
        cfg.set("MegaPlot", {"conventional bscans":self.conventional_bscans})
        self.update_plot()

    @replace_plot
    def on_rectify(self, evt):
        """Handles request to apply rectification to A-scan plot"""
        xpos = self.view.xpos_sc.GetValue()
        ypos = self.view.ypos_sc.GetValue()
        self.plot_ascan(self.model.rectify_full(self.scnr.ascan_data(xpos, ypos)), xpos, ypos)

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
                    module_logger.error("Unable to generate C-scan: {0}".format(err))
                    err_msg = "{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Generate C Scan", style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                finally:
                    rng_dlg.Destroy()