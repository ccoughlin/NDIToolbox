"""test_ndescanhandler.py - tests the ndescanhandler module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import ndescanhandler
import numpy as np
import random
import unittest

class TestNDEScanHandler(unittest.TestCase):
    """Tests the NDEScanHandler class"""

    def setUp(self):
        self.threed_array = self.random3D_data()
        self.min_x = 0
        self.max_x = self.threed_array.shape[1] - 1
        self.min_y = 0
        self.max_y = self.threed_array.shape[0] - 1
        self.min_z = 0
        self.max_z = self.threed_array.shape[2] - 1
        self.scnr = ndescanhandler.NDEScanHandler(self.threed_array)

    def random3D_data(self):
        """Generates a random 3D array of data"""
        raw_array = np.array([random.uniform(-100, 100) for i in range(24)])
        three_d_array = raw_array.reshape((3, 2, 4))
        return three_d_array

    def test_dimcheck(self):
        """Verify NDEScanHandler rejects arrays that are not 3D"""
        oned_arr = np.zeros([5])
        with self.assertRaises(AssertionError):
            scnr = ndescanhandler.NDEScanHandler(oned_arr)

    def test_cscan_data(self):
        """Verify returning a single 2D slice from a 3D array"""
        random_slices = [random.uniform(0, self.threed_array.shape[2]) for i in range(2)]
        for slice_idx in random_slices:
            expected_array = self.threed_array[:, :, slice_idx]
            returned_slice = self.scnr.cscan_data(slice_idx)
            self.assertTrue(np.array_equal(expected_array, returned_slice))

    def test_ascan_data(self):
        """Verify returning a complete waveform from a given (x,y) position"""
        for i in range(10):
            xpos = random.randint(self.min_x, self.max_x)
            ypos = random.randint(self.min_y, self.max_y)
            expected_waveform = self.threed_array[ypos, xpos, :]
            returned_waveform = self.scnr.ascan_data(xpos, ypos)
            self.assertTrue(np.array_equal(expected_waveform, returned_waveform))

    def test_horizontalslice_bscan_data(self):
        """Verify returning the horizontal B Scan from the C Scan
        (1D slice at constant y from the 2D NumPy array)."""
        slice_idx = random.randint(self.min_z, self.max_z)
        for ypos in range(self.min_y, self.max_y):
            expected_slice = self.threed_array[ypos, :, slice_idx]
            returned_bscan = self.scnr.hslice_cscan_data(slice_idx, ypos)
            self.assertTrue(np.array_equal(expected_slice, returned_bscan))

    def test_verticalslice_bscan_data(self):
        """Verify returning the vertical B Scan from the C Scan
        (1D slice at constant x from the 2D NumPy array)."""
        slice_idx = random.randint(self.min_z, self.max_z)
        for xpos in range(self.min_x, self.max_x):
            expected_slice = self.threed_array[:, xpos, slice_idx]
            returned_bscan = self.scnr.vslice_cscan_data(slice_idx, xpos)
            self.assertTrue(np.array_equal(expected_slice, returned_bscan))

    def test_hbscan_data(self):
        """Verify returning a planar slice from the 3D data at the given y position."""
        slice_idx = random.randint(self.min_y, self.max_y)
        expected_slice = self.scnr.data[slice_idx, :, :]
        self.assertTrue(np.array_equal(expected_slice, self.scnr.hbscan_data(slice_idx)))

    def test_vbscan_data(self):
        """Verify returning a planar slice from the 3D data at the given x position."""
        slice_idx = random.randint(self.min_x, self.max_x)
        expected_slice = self.scnr.data[:, slice_idx, :]
        self.assertTrue(np.array_equal(expected_slice, self.scnr.vbscan_data(slice_idx)))

    def test_gen_cscan(self):
        """Verify returning a 2D array based on a supplied
        operation"""
        start_idx = random.randint(self.min_z, self.max_z)
        stop_idx = random.randint(self.min_z, self.max_z)
        if stop_idx < start_idx:
            tmp_idx = start_idx
            start_idx = stop_idx
            stop_idx = tmp_idx
        elif stop_idx == start_idx:
            start_idx = 0
            stop_idx = self.max_z
        available_ops = [np.amax, np.amin, np.ptp, np.average, np.mean, np.median]
        for op in available_ops:
            expected_result = op(self.threed_array[:, :, start_idx:stop_idx], axis=2)
            returned_result = self.scnr.gen_cscan(start_idx, stop_idx, op)
            self.assertTrue(np.array_equal(expected_result, returned_result))

if __name__ == "__main__":
    random.seed()
    unittest.main()