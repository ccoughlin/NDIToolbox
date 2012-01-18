"""plotwindow_ctrl.py - defines the controller for plotwindow.py

Chris R. Coughlin (TRI/Austin, Inc.)
"""
from matplotlib import cm

__author__ = 'Chris R. Coughlin'

from views import dialogs
from models import mainmodel
import models.plotwindow_model as model
import wx
import wx.lib.dialogs
from functools import wraps

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

class BasicPlotWindowController(object):
    """Base class for PlotWindows"""

    def __init__(self, view):
        self.view = view
        self.axes_grid = True
        self.model = model.BasicPlotWindowModel(self)

    @property
    def data(self):
        return self.model.data

    @property
    def original_data(self):
        return self.model.original_data

    def refresh_plot(self):
        """Forces plot to redraw itself"""
        self.view.canvas.draw()

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
        """Loads the data from the specified file name"""
        import_dlg = dialogs.ImportTextDialog(parent=self.view.parent)
        if import_dlg.ShowModal() == wx.ID_OK:
            readtext_parameters = import_dlg.get_import_parameters()
            self.model.original_data = mainmodel.get_data(data_file, **readtext_parameters)
            self.model.revert_data()

class PlotWindowController(BasicPlotWindowController):
    """Controller for PlotWindow class"""

    def __init__(self, view):
        self.view = view
        self.axes_grid = True
        self.model = model.PlotWindowModel(self)

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
                start_pos, end_pos = rng_dlg.GetValue()
                self.model.apply_gate(gate_id, start_pos, end_pos)
            rng_dlg.Destroy()

class ImgPlotWindowController(BasicPlotWindowController):
    """Controller for ImgPlotWindow class"""

    def __init__(self, view):
        self.view = view
        self.axes_grid = True
        self.model = model.ImgPlotWindowModel(self)
        self.colormap = cm.get_cmap('Spectral')
        self.colorbar = None

    def plot(self, data):
        """Plots the dataset"""
        if data is not None:
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