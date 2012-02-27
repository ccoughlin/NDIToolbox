"""plotwindow_model.py - Model for plotwindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""
from matplotlib import cm

__author__ = 'Chris R. Coughlin'

import mainmodel
import numpy as np
import scipy.signal

class BasicPlotWindowModel(object):
    """Model for the BasicPlotWindow"""

    def __init__(self, controller, data_file, **read_text_params):
        self.controller = controller
        self.data_file = data_file
        self.read_parameters = read_text_params
        self.original_data = None
        self.data = None

    def load_data(self):
        """Loads the data from the instance's data file"""
        self.original_data = mainmodel.get_data(self.data_file, **self.read_parameters)
        self.revert_data()

    def revert_data(self):
        """Reverts to original data set"""
        self.data = np.array(self.original_data)

    def get_plugins(self):
        """Returns a list of available plugins"""
        return mainmodel.load_plugins()


class PlotWindowModel(BasicPlotWindowModel):
    """Model for the PlotWindow"""

    def __init__(self, controller, data_file, **read_text_params):
        super(PlotWindowModel, self).__init__(controller, data_file, **read_text_params)
        self._define_gate_functions()

    def _define_gate_functions(self):
        """Define a set of gate functions that can be applied to the data
        dict format - keys are names of the actual gate function
        vals are a tuple of the gate function label and a wxPython
        id to assign to the menu item
        """
        self.gates = dict(boxcar=('Boxcar', 1000), triang=('Triangular', 1001),
            blackman=('Blackman', 1002),
            hamming=('Hamming', 1003), hanning=('Hann (Hanning)', 1004),
            bartlett=('Bartlett', 1005),
            parzen=('Parzen', 1006), bohman=('Bohman', 1007),
            blackmanharris=('Blackman-Harris', 1008),
            nuttall=('Nuttall', 1009), barthann=('Barthann', 1010))

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

    def apply_gate(self, gate_id, start_pos, end_pos):
        """Applies a window function ('gate' in ultrasonics parlance)
        to the current data set"""
        if self.data is not None:
            gate_fn = None
            for gate_idx, params in self.gates.items():
                if params[1] == gate_id:
                    gate_fn = self.gates[gate_idx]
            if gate_fn is not None:
                if self.data.ndim == 1:
                    self.data = self.apply_window(gate_fn, self.data, start_pos, end_pos)
                elif self.data.ndim == 2:
                    # Find appropriate indices for specified range
                    x_data = np.sort(self.data[0])
                    start_idx = np.searchsorted(x_data, start_pos)
                    end_idx = np.searchsorted(x_data, end_pos)
                    self.data[1] = self.apply_window(gate_fn, self.data[1], start_idx, end_idx)

    def rectify_full(self):
        """Sets current data set to absolute value
        (full rectification in ultrasonics parlance)"""
        self.data = np.absolute(self.data)


class ImgPlotWindowModel(BasicPlotWindowModel):
    """Model for the ImgPlotWindow"""

    def __init__(self, controller, data_file, **read_text_params):
        super(ImgPlotWindowModel, self).__init__(controller, data_file, **read_text_params)

    def detrend_data(self, axis, type):
        """Applies a detrend (where type is 'constant' for average or 'linear')
        to the data along the specified axis number."""
        if self.data is not None:
            self.data = scipy.signal.detrend(self.data, axis, type)

    def generate_colormap_strip(self):
        """Returns a NumPy ndarray suitable for displaying a colormap.
        Used to provide a preview of available matplotlib colormaps."""
        a = np.linspace(0, 1, 256).reshape(1, -1)
        a = np.vstack((a, a))
        return a

    def get_colormap_choices(self):
        """Returns a list of the available imgplot colormaps"""
        cmap_choices = [m for m in cm.datad if not m.endswith("_r")]
        cmap_choices.sort()
        return cmap_choices