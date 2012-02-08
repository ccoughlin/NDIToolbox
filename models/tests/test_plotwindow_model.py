"""test_plotwindow_model.py - tests the plotwindow_model module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import models.plotwindow_model as model
import models.mainmodel as mainmodel
import models.abstractplugin as abstractplugin
import numpy as np
import scipy.signal
import unittest

class TestBasicPlotWindowModel(unittest.TestCase):
    """Tests the BasicPlotWindowModel class"""

    def setUp(self):
        self.mock_controller = ""
        self.mock_data_file = ""
        self.mock_read_parameters = {}
        self.basic_model = model.BasicPlotWindowModel(self.mock_controller,
            self.mock_data_file, **self.mock_read_parameters)

    def test_revert_data(self):
        """Verify data is reverted to original"""
        original_data = np.array([1, 3, 5, 7, 9])
        self.assertIsNone(self.basic_model.original_data)
        self.assertIsNone(self.basic_model.data)
        self.basic_model.original_data = original_data
        self.basic_model.data = np.ones(5)
        self.basic_model.revert_data()
        self.assertListEqual(self.basic_model.original_data.tolist(), original_data.tolist())
        self.assertListEqual(self.basic_model.original_data.tolist(), self.basic_model.data.tolist())

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


class TestPlotWindowModel(unittest.TestCase):
    """Tests the PlotWindowModel class"""

    def setUp(self):
        self.mock_controller = ""
        self.mock_data_file = ""
        self.mock_read_parameters = {}
        self.model = model.PlotWindowModel(self.mock_controller, self.mock_data_file,
            **self.mock_read_parameters)

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
        original_data = np.ones(55)
        for gate in self.model.gates:
            gate_fn = gate[0]
            windowed_data = self.model.apply_window(gate_fn, original_data, 3, 21)
            self.assertTrue(isinstance(windowed_data, np.ndarray))
            self.assertEqual(original_data.size, windowed_data.size)

    def test_apply_gate(self):
        """Verify apply_gate function"""
        original_data = np.ones(6)
        self.model.original_data = original_data
        for gate in self.model.gates:
            self.model.revert_data()
            gate_fn = self.model.gates.get(gate)[0]
            gate_id = self.model.gates.get(gate)[1]
            start_idx = 2
            end_idx = 4
            expected_data = self.model.apply_window(gate_fn, self.model.data,
                start_idx, end_idx)
            self.model.apply_gate(gate_id, start_idx, end_idx)
            self.assertListEqual(original_data.tolist(), self.model.original_data.tolist())
            self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_rectify_full(self):
        """Verify full rectification of data"""
        raw_data = []
        for i in range(-5, 6):
            raw_data.append(i)
        original_data = np.array(raw_data)
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
        self.model = model.ImgPlotWindowModel(self.mock_controller, self.mock_data_file,
            **self.mock_read_parameters)

    def test_average_detrend(self):
        """Verify mean detrending along an axis"""
        self.model.original_data = np.array([-1, 3.1, -5, 7.5, -9, 11.9])
        self.model.revert_data()
        expected_data = scipy.signal.detrend(self.model.original_data, type='constant')
        self.model.detrend_data(0, 'constant')
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

    def test_linear_detrend(self):
        """Verify linear detrending along an axis"""
        self.model.original_data = np.array([2.0, -1, 4.2, -3, 6.4, -5, 8.6, -7])
        self.model.revert_data()
        expected_data = scipy.signal.detrend(self.model.original_data, type='linear')
        self.model.detrend_data(0, 'linear')
        self.assertListEqual(expected_data.tolist(), self.model.data.tolist())

if __name__ == "__main__":
    unittest.main()