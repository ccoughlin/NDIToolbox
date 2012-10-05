"""plotwindow_model.py - Model for plotwindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""
from matplotlib import cm

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
import dataio
import mainmodel
import ultrasonicgate
import numpy as np
import scipy.signal

class TwoDManipMixin(object):
    """Mixin class to provide data manipulation routines for one or two dimensional data sets"""

    def load_user_gate_functions(self):
        """Retrieves the user-created ultrasonic gate functions and returns a list
        of tuples (gate_function_name, gate_function_class_instance)."""
        return mainmodel.load_dynamic_modules(pathfinder.gates_path(), ultrasonicgate.UltrasonicGate)

    def _define_gate_functions(self):
        """Define a set of gate functions that can be applied to the data
        dict format - keys are names of the actual gate function
        vals are a tuple of the gate function label and a wxPython
        id to assign to the menu item
        """
        self.gates = self.load_user_gate_functions()
        self.gates.sort()

    def apply_window(self, window_type, original_data, start_idx, end_idx):
        """Returns the specified type of window for the range
        start_idx:end_idx, zero outside.  For squelching data outside
        the given range."""
        gate_names = [_gate[0] for _gate in self.gates]
        gates = [_gate[1] for _gate in self.gates]
        gate_cls = gates[gate_names.index(window_type)]
        gate = gate_cls(start_pos=start_idx, end_pos=end_idx)
        gate.data = original_data
        gate.run()
        return gate.data

    def apply_gate(self, data, gate, start_pos, end_pos):
        """Applies a window function ('gate' in ultrasonics parlance)
        to the current data set"""
        if data is not None:
            if data.ndim == 1:
                data = self.apply_window(gate, data, start_pos, end_pos)
            elif data.ndim == 2:
                # Find appropriate indices for specified range
                x_data = np.sort(data[0])
                start_idx = np.searchsorted(x_data, start_pos)
                end_idx = np.searchsorted(x_data, end_pos)
                data[1] = self.apply_window(gate, data[1], start_idx, end_idx)
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
        self.original_data = dataio.get_data(self.data_file)
        self.revert_data()

    def revert_data(self):
        """Reverts to original data set"""
        self.data = self.original_data

    def get_plugins(self):
        """Returns a list of available plugins"""
        return mainmodel.load_plugins()

    def get_plugin(self, plugin_name):
        """Given the name of a plugin, returns the plugin's class
        or None if the plugin isn't listed in the available plugins."""
        plugin_class = None
        available_plugins = self.get_plugins()
        plugin_names = [plugin[0] for plugin in available_plugins]
        plugin_classes = [plugin[1] for plugin in available_plugins]
        if plugin_name in plugin_names:
            plugin_class = plugin_classes[plugin_names.index(plugin_name)]
        return plugin_class


class PlotWindowModel(BasicPlotWindowModel, TwoDManipMixin):
    """Model for the PlotWindow"""

    def __init__(self, controller, data_file):
        super(PlotWindowModel, self).__init__(controller, data_file)
        self._define_gate_functions()

    def get_gates(self):
        """Returns a list of available plugins"""
        return mainmodel.load_gates()

    def get_gate(self, gate_name):
        """Given the name of a plugin, returns the plugin's class
        or None if the plugin isn't listed in the available plugins."""
        gate_cls = None
        available_gates = self.get_gates()
        gate_names = [gate[0] for gate in available_gates]
        gate_classes = [gate[1] for gate in available_gates]
        if gate_name in gate_names:
            gate_cls = gate_classes[gate_names.index(gate_name)]
        return gate_cls

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