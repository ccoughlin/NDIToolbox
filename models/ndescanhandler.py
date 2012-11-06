"""ndescanhandler.py - returns A, B, and C scan datasets
from three-dimensional NumPy arrays

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import numpy as np

class NDEScanHandler(object):
    """Utility class to return A, B, and C scan
    arrays from three-dimensional NDE scans"""

    def __init__(self, np_array):
        """Creates the array handler from the specified
        NumPy array.  Raises AssertionError if np_array
        does not have three dimensions."""
        assert np_array.ndim == 3
        self.data = np_array

    @property
    def available_cscan_functions(self):
        """Returns a list of functions currently available to
        generate a C-scan array from a 3D array"""
        return [np.amax, np.amin, np.ptp, np.average, np.mean, np.median]

    @property
    def available_cscan_function_names(self):
        """Returns a human-friendly list of function names available
        to generate a C-scan array from a 3D array"""
        return ["Maximum", "Minimum", "Peak-To-Peak", "Weighted Average", "Mean", "Median"]

    def cscan_data(self, slice_idx):
        """Returns the 2D slice of the 3D array
        at index z=slice_idx."""
        return self.data[:, :, slice_idx]

    def ascan_data(self, xpos, ypos):
        """Returns the waveform from the (x,y) position"""
        return self.data[ypos, xpos, :]

    def hslice_cscan_data(self, slice_idx, ypos):
        """Returns the horizontal slice at y=ypos through the 2D slice at z=slice_idx (1D cross-section through the
        C-scan at specified Z index)."""
        # TODO: replace with single operation
        # self.data[ypos, :, slice_idx]
        # when initial testing complete
        cscan_data = self.cscan_data(slice_idx)
        return cscan_data[ypos, :]

    def hbscan_data(self, y_idx):
        """Returns the 2D planar slice at the specified Y position through the 3D data."""
        return self.data[y_idx, :, :]

    def vslice_cscan_data(self, slice_idx, xpos):
        """Returns the vertical slice at x=xpos through the 2D slice at z=slice_idx (1D cross-section through the
        C-scan at specified Z index)."""
        # TODO: replace with single operation
        # self.data[:, xpos, slice_idx]
        # when initial testing complete
        cscan_data = self.cscan_data(slice_idx)
        return cscan_data[:, xpos]

    def vbscan_data(self, x_idx):
        """Returns the 2D planar slice at the specified X position through the 3D data."""
        return self.data[:, x_idx, :]

    def gen_cscan(self, start_idx, stop_idx, fn=None):
        """Returns a computed C scan dataset:  takes the subset
        of data between z=start_idx and z=stop_idx and applies a
        function to return a computed 2D array.  Raises an
        AssertionError if stop_idx <= start_idx.

        Function defaults to numpy.amax if not provided and must be
        one of the following functions that support an axis argument:
        [np.amax, np.amin, np.ptp, np.average, np.mean, np.median].
        """
        assert stop_idx > start_idx
        data = self.data[:, :, start_idx:stop_idx]
        if fn is None:
            cscan_data = np.amax(data, axis=2)
        else:
            assert fn in self.available_cscan_functions
            cscan_data = fn(data, axis=2)
        return cscan_data