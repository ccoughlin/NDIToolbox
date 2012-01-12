"""plotwindow_ctrl.py - defines the controller for plotwindow.py

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from views import ui_defaults
from views import dialogs
from models import mainmodel
import numpy as np
import wx

class PlotWindowController(object):
    """Controller for PlotWindow class"""

    def __init__(self, view):
        self.view = view
        self.original_data = None
        self.data = None
        self._define_gate_functions()

    def load_data(self, data_file):
        """Loads the data from the specified file name"""
        import_dlg = dialogs.ImportTextDialog(parent=self.view.parent)
        if import_dlg.ShowModal() == wx.ID_OK:
            readtext_parameters = import_dlg.get_import_parameters()
            self.original_data = mainmodel.get_data(data_file, **readtext_parameters)
            self.revert_data()

    def revert_data(self):
        """Reverts to original data set"""
        self.data = np.array(self.original_data)

    def apply_gate(self, gate_id):
        """Applies a window function ('gate' in ultrasonics parlance)
        to the current data set"""
        if self.data is not None:
            gate_fn = None # Window function to apply to the data
            rng_dlg = dialogs.FloatRangeDialog("Please specify the gate region.")
            if rng_dlg.ShowModal() == wx.ID_OK:
                start_pos, end_pos = rng_dlg.GetValue()
                # Find appropriate indices for specified range
                x_data = np.sort(self.data[0])
                start_idx = np.searchsorted(x_data, start_pos)
                end_idx = np.searchsorted(x_data, end_pos)
                for gate in self.gates:
                    if gate[1] == gate_id:
                        gate_fn = gate
                if gate_fn is not None:
                    if self.data.ndim == 1:
                        self.data = self.model.apply_window(gate_fn, self.data, start_idx, end_idx)
                    elif self.data.ndim == 2:
                        self.data[1] = self.model.apply_window(gate_fn, self.data[1], start_idx, end_idx)
            rng_dlg.Destroy()

    def _define_gate_functions(self):
        """Define a set of gate functions that can be applied to the data
        dict format - keys are names of the actual gate function
        vals are a tuple of the gate function label and a wxPython
        id to assign to the menu item
        """
        self.gates = dict(boxcar=('Boxcar', 1000), triang=('Triangular', 1001), blackman=('Blackman', 1002),
                          hamming=('Hamming', 1003), hanning=('Hann (Hanning)', 1004), bartlett=('Bartlett', 1005),
                          parzen=('Parzen', 1006), bohman=('Bohman', 1007), blackmanharris=('Blackman-Harris', 1008),
                          nuttall=('Nuttall', 1009), barthann=('Barthann', 1010))