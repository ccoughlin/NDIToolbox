"""test_plotwindow_model.py - tests the plotwindow_model module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import models.plotwindow_model as model
import models.mainmodel as mainmodel
import models.abstractplugin as abstractplugin
import numpy as np
import scipy.signal
import random
import unittest

class TestBasicPlotWindowModel(unittest.TestCase):
    """Tests the BasicPlotWindowModel class"""

    def setUp(self):
        self.mock_controller = ""
        self.mock_data_file = ""
        self.basic_model = model.BasicPlotWindowModel(self.mock_controller,
                                                      self.mock_data_file)

    def random_data(self):
        """Returns a list of random data"""
        return [random.uniform(-100, 100) for i in range(25)]

    def test_revert_data(self):
        """Verify data is reverted to original"""
        original_data = np.array(self.random_data())
        self.assertIsNone(self.basic_model.original_data)
        self.assertIsNone(self.basic_model.data)
        self.basic_model.original_data = original_data
        self.basic_model.data = np.array(self.random_data())
        self.basic_model.revert_data()
        self.assertListEqual(self.basic_model.original_data.tolist(), original_data.tolist())
        self.assertListEqual(self.basic_model.original_data.tolist(),
                             self.basic_model.data.tolist())

    def test_get_plugins(self):
        """Verify a list of available plugins is returned"""
        expected_plugin_list = mainmodel.load_plugins()
        expected_plugin_names = [plugin[0] for plugin in expected_plugin_list]
        retrieved_plugin_list = self.basic_model.get_plugins()
        self.assertEqual(len(expected_plugin_list), len(retrieved_plugin_list))
        for plugin in retrieved_plugin_list:
            plugin_name = plugin[0]
            plugin_instance = plugin[1]
            self.assertTrue(plugin_name in expected_plugin_names)
            self.assertTrue(issubclass(plugin_instance, abstractplugin.AbstractPlugin))

    def test_get_plugin(self):
        """Verify a class name and an instance of a plugin is returned"""
        retrieved_plugin_list = self.basic_model.get_plugins()
        for plugin in retrieved_plugin_list:
            plugin_name = plugin[0]
            plugin_instance = plugin[1]
            plg_cls, plg_instance = self.basic_model.get_plugin(plugin_name)
            self.assertEqual(type(plugin_instance), type(plg_cls))
            self.assertTrue(isinstance(plg_instance, plg_cls))


class TestPlotWindowModel(unittest.TestCase):
    """Tests the PlotWindowModel class"""

    def setUp(self):
        self.mock_controller = ""
        self.mock_data_file = ""
        self.model = model.PlotWindowModel(self.mock_controller, self.mock_data_file)

    def random_data(self):
        """Returns a list of random data"""
        return [random.uniform(-100, 100) for i in range(25)]

    def test_define_gate_functions(self):
        """Verify _define_gate_functions sets up a dict of available window functions"""
        self.assertTrue(isinstance(self.model.gates, dict))
        available_gate_functions = ("boxcar", "triang", "blackman", "hamming",
                                    "hanning", "bartlett", "parzen", "bohman",
                                    "blackmanharris", "nuttall", "barthann")
        for gate_fn in available_gate_functions:
            self.assertTrue(gate_fn in self.model.gates)

    def test_apply_window(self):
        """Verify apply_window function applies a given gate function and returns an ndarray"""
        #original_data = np.ones(55)
        original_data = np.array(self.random_data())
        for gate in self.model.gates:
            gate_fn = gate[0]
            windowed_data = self.model.apply_window(gate_fn, original_data, 3, 21)
            self.assertTrue(isinstance(windowed_data, np.ndarray))
            self.assertEqual(original_data.size, windowed_data.size)

    def test_apply_gate(self):
        """Verify apply_gate function"""
        original_data = np.array(self.random_data())
        self.model.original_data = original_data
        for gate in self.model.gates:
            self.model.revert_data()
            gate_fn = self.model.gates.get(gate)[0]
            gate_id = self.model.gates.get(gate)[1]
            start_idx = 2
            end_idx = 4
            expected_data = model.TwoDManipMixin().apply_window(gate_fn, self.model.data,
                                                    start_idx, end_idx)
            self.model.apply_gate(gate_id, start_idx, end_idx)
            self.assertListEqual(original_data.tolist(), self.model.original_data.tolist())
            self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_rectify_full(self):
        """Verify full rectification of data"""
        original_data = np.array(self.random_data())
        self.model.original_data = original_data
        self.model.revert_data()
        self.model.rectify_full()
        self.assertListEqual(np.absolute(original_data).tolist(), self.model.data.tolist())


class TestImgPlotWindowModel(unittest.TestCase):
    """Tests the ImgPlotWindowModel class"""

    def setUp(self):
        self.mock_controller = ""
        self.mock_data_file = ""
        self.mock_read_parameters = {}
        self.model = model.ImgPlotWindowModel(self.mock_controller, self.mock_data_file)

    def random_data(self):
        """Generates a random list of data"""
        return np.array([random.uniform(-100, 100) for i in range(25)])

    def random3D_data(self):
        """Generates a random 3D array of data"""
        raw_array = np.array([random.uniform(-100, 100) for i in range(24)])
        three_d_array = raw_array.reshape((3, 2, 4))
        return three_d_array

    def test_average_detrend(self):
        """Verify mean detrending along an axis"""
        self.model.original_data = self.random_data()
        self.model.revert_data()
        expected_data = scipy.signal.detrend(self.model.original_data, type='constant')
        self.model.detrend_data(0, 'constant')
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_linear_detrend(self):
        """Verify linear detrending along an axis"""
        self.model.original_data = self.random_data()
        self.model.revert_data()
        expected_data = scipy.signal.detrend(self.model.original_data, type='linear')
        self.model.detrend_data(0, 'linear')
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_slice_data(self):
        """Verify a 3D array is replaced by a 2D slice"""
        three_d_array = self.random3D_data()
        self.model.original_data = three_d_array
        self.model.revert_data()
        slice_idx = random.choice(range(three_d_array.shape[2]))
        expected_data = three_d_array[:, :, slice_idx]
        self.model.slice_data(slice_idx)
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_flipud_data(self):
        """Verify data are flipped vertically"""
        self.model.original_data = self.random_data()
        self.model.revert_data()
        expected_data = np.flipud(self.model.data)
        self.model.flipud_data()
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_fliplr_data(self):
        """Verify data are flipped horizontally"""
        three_d_array = self.random3D_data()
        self.model.original_data = np.array(three_d_array)
        self.model.revert_data()
        expected_data = np.fliplr(self.model.data)
        self.model.fliplr_data()
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_rotate_data(self):
        """Verify data are rotated counter-clockwise"""
        self.model.original_data = self.random3D_data()
        self.model.revert_data()
        num_rotations = random.choice((1, 2, 3))
        expected_data = np.rot90(self.model.data, k=num_rotations)
        self.model.rotate_data(num_rotations)
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_transpose_data(self):
        """Verify data are transposed"""
        self.model.original_data = self.random3D_data()
        self.model.revert_data()
        expected_data = self.model.data.T
        self.model.transpose_data()
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

if __name__ == "__main__":
    random.seed()
    unittest.main()