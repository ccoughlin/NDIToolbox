"""plotwindow_model.py - Model for plotwindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""
from matplotlib import cm

__author__ = 'Chris R. Coughlin'

import mainmodel
import numpy as np
import scipy.signal

class TwoDManipMixin(object):
    """Mixin class to provide data manipulation routines for one or two dimensional data sets"""

    def _define_gate_functions(self):
        """Define a set of gate functions that can be applied to the data
        dict format - keys are names of the actual gate function
        vals are a tuple of the gate function label and a wxPython
        id to assign to the menu item
        """
        self.gates = dict(boxcar=('Boxcar', 10000), triang=('Triangular', 10001),
                          blackman=('Blackman', 10002),
                          hamming=('Hamming', 10003), hanning=('Hann (Hanning)', 10004),
                          bartlett=('Bartlett', 10005),
                          parzen=('Parzen', 10006), bohman=('Bohman', 10007),
                          blackmanharris=('Blackman-Harris', 10008),
                          nuttall=('Nuttall', 10009), barthann=('Barthann', 10010))

    def apply_window(self, window_type, original_data, start_idx, end_idx):
        """Returns the specified type of window for the range
        start_idx:end_idx, zero outside.  For squelching data outside
        the given range."""
        left = np.zeros(start_idx)
        windows = ['boxcar', 'triang', 'blackman', 'hamming', 'hanning', 'bartlett',
                   'parzen', 'bohman', 'blackmanharris', 'nuttall', 'barthann']
        if window_type not in windows:
            middle = np.ones(end_idx - start_idx)
        else:
            middle = scipy.signal.get_window(window_type, end_idx - start_idx)
        right = np.zeros(original_data.shape[0] - end_idx)
        winder = np.concatenate((left, middle, right))
        data = np.multiply(original_data, winder)
        return data

    def apply_gate(self, data, gate_id, start_pos, end_pos):
        """Applies a window function ('gate' in ultrasonics parlance)
        to the current data set"""
        if data is not None:
            gate_fn = None
            for gate_idx, params in self.gates.items():
                if params[1] == gate_id:
                    gate_fn = self.gates[gate_idx]
            if gate_fn is not None:
                if data.ndim == 1:
                    data = self.apply_window(gate_fn, data, start_pos, end_pos)
                elif data.ndim == 2:
                    # Find appropriate indices for specified range
                    x_data = np.sort(data[0])
                    start_idx = np.searchsorted(x_data, start_pos)
                    end_idx = np.searchsorted(x_data, end_pos)
                    data[1] = self.apply_window(gate_fn, data[1], start_idx, end_idx)
        return data

    def rectify_full(self, data):
        """Sets current data set to absolute value
        (full rectification in ultrasonics parlance)"""
        if data is not None:
            data = np.absolute(data)
        return data

class ThreeDManipMixin(object):
    """Mixin class to provide data manipulation routines for three dimensional data sets"""

    def slice_data(self, data, slice_idx):
        """Sets the 3D self.data to a single 2D slice."""
        if data is not None:
            if data.ndim == 3:
                min_slice_idx = 0
                max_slice_idx = data.shape[2]-1
                data = data[:, :, slice_idx]
        return data

    def detrend_data(self, data, axis, type):
        """Applies a detrend (where type is 'constant' for average or 'linear')
        to the data along the specified axis number."""
        if data is not None:
            data = scipy.signal.detrend(data, axis, type)
        return data

    def flipud_data(self, data):
        """Flips the data vertically"""
        if data is not None:
            data = np.flipud(data)
        return data

    def fliplr_data(self, data):
        """Flips the data horizontally"""
        if data is not None:
            data = np.fliplr(data)
        return data

    def rotate_data(self, data, num_rotations=1):
        """Rotates the data 90 degrees counterclockwise for
        each count in num_rotations (defaults to 1 rotation)"""
        if data is not None:
            data = np.rot90(data, num_rotations)
        return data

    def transpose_data(self, data):
        """Transposes the data, i.e. an array Aij with i
        rows and j columns becomes an array A'ji with j
        rows and i columns."""
        if data is not None:
            data = data.T
        return data

    def generate_colormap_strip(self):
        """Returns a NumPy ndarray suitable for displaying a colormap.
        Used to provide a preview of available matplotlib colormaps."""
        a = np.linspace(0, 1, 256).reshape(1, -1)
        a = np.vstack((a, a))
        return a

    def get_colormap_choices(self):
        """Returns a list of the available imgplot colormaps"""
        cmap_choices = [m for m in cm.datad]
        cmap_choices.sort()
        return cmap_choices

class BasicPlotWindowModel(object):
    """Model for the BasicPlotWindow"""

    def __init__(self, controller, data_file):
        self.controller = controller
        self.data_file = data_file
        self.original_data = None
        self.data = None

    def load_data(self):
        """Loads the data from the instance's data file"""
        self.original_data = mainmodel.get_data(self.data_file)
        self.revert_data()

    def revert_data(self):
        """Reverts to original data set"""
        self.data = self.original_data

    def get_plugins(self):
        """Returns a list of available plugins"""
        return mainmodel.load_plugins()

    def get_plugin(self, plugin_name):
        """Given the name of a plugin, returns the plugin's class and an instance of the plugin,
        or (None, None) if the plugin isn't listed in the available plugins."""
        plugin_class = None
        plugin_instance = None
        available_plugins = self.get_plugins()
        plugin_names = [plugin[0] for plugin in available_plugins]
        plugin_classes = [plugin[1] for plugin in available_plugins]
        if plugin_name in plugin_names:
            plugin_class = plugin_classes[plugin_names.index(plugin_name)]
            plugin_instance = plugin_class()
            plugin_instance.data = self.data
        return plugin_class, plugin_instance


class PlotWindowModel(BasicPlotWindowModel, TwoDManipMixin):
    """Model for the PlotWindow"""

    def __init__(self, controller, data_file):
        super(PlotWindowModel, self).__init__(controller, data_file)
        self._define_gate_functions()

    def apply_gate(self, gate_id, start_pos, end_pos):
        """Applies the specified gate ID to the current data set in the region
        mapped out between start_pos and end_pos indices"""
        self.data = super(PlotWindowModel, self).apply_gate(self.data, gate_id, start_pos, end_pos)

    def rectify_full(self):
        """Sets current data set to absolute value
        (full rectification in ultrasonics parlance)"""
        self.data = super(PlotWindowModel, self).rectify_full(self.data)

class ImgPlotWindowModel(BasicPlotWindowModel, ThreeDManipMixin):
    """Model for the ImgPlotWindow"""

    def __init__(self, controller, data_file):
        super(ImgPlotWindowModel, self).__init__(controller, data_file)

    def slice_data(self, slice_idx):
        """Sets the 3D self.data to a single 2D slice."""
        self.data = super(ImgPlotWindowModel, self).slice_data(self.data, slice_idx)

    def detrend_data(self, axis, type):
        """Applies a detrend (where type is 'constant' for average or 'linear')
        to the data along the specified axis number."""
        self.data = super(ImgPlotWindowModel, self).detrend_data(self.data, axis, type)

    def flipud_data(self):
        """Flips the data vertically"""
        self.data = super(ImgPlotWindowModel, self).flipud_data(self.data)

    def fliplr_data(self):
        """Flips the data horizontally"""
        self.data = super(ImgPlotWindowModel, self).fliplr_data(self.data)

    def rotate_data(self, num_rotations=1):
        """Rotates the data 90 degrees counterclockwise for
        each count in num_rotations (defaults to 1 rotation)"""
        self.data = super(ImgPlotWindowModel, self).rotate_data(self.data, num_rotations)

    def transpose_data(self):
        """Transposes the data, i.e. an array Aij with i
        rows and j columns becomes an array A'ji with j
        rows and i columns."""
        self.data = super(ImgPlotWindowModel, self).transpose_data(self.data)

class MegaPlotWindowModel(BasicPlotWindowModel, TwoDManipMixin, ThreeDManipMixin):
    """Model for the MegaPlotWindow"""

    def __init__(self, controller, data_file):
        super(MegaPlotWindowModel, self).__init__(controller, data_file)
        self._define_gate_functions()

