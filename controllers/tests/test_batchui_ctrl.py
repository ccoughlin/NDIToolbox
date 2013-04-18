"""test_batchui_ctrl.py - tests the batchui_ctrl module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

import unittest
from models import dataio
from models import mainmodel
from controllers import pathfinder
from controllers import batchui_ctrl
import numpy as np
import os
import random
import tempfile


class TestBatchUIController(unittest.TestCase):
    """Tests the batchui_ctrl functions"""

    def test_available_file_types(self):
        """Verify returning a list of the currently supported filetypes"""
        expected_list = batchui_ctrl.file_types.keys()
        self.assertListEqual(expected_list, batchui_ctrl.available_file_types())

    def test_get_file_type(self):
        """Verify returning the assumed filetype"""
        base_fname = os.path.join(os.path.dirname(__file__), "test")
        for ftype in batchui_ctrl.file_types.keys():
            for ext in batchui_ctrl.file_types[ftype]:
                fname = base_fname + ext
                self.assertEqual(ftype, batchui_ctrl.get_file_type(fname))
        # Confirm unknown extensions return no match
        unknown_fname = base_fname + ".qqq"
        self.assertIsNone(batchui_ctrl.get_file_type(unknown_fname))


class TestBatchPluginAdapter(unittest.TestCase):
    """Tests the BatchPluginAdapter class"""

    def setUp(self):
        self.toolkit_class = "MedianFilterPlugin"
        self.datafile = self.create_datafile() # Sample HDF5 data file

    def tearDown(self):
        if os.path.exists(self.datafile):
            try:
                os.remove(self.datafile)
            except WindowsError: # file in use (Windows)
                pass
            except OSError: # other OS error
                pass

    def create_datafile(self, ext=".hdf5"):
        """Returns a NamedTemporaryFile containing NumPy data.  Caller responsible for deletion."""
        temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        rnd_data = [random.uniform(-5, 5) for i in range(11)]
        dataio.save_data(temp_file.name, np.array(rnd_data))
        return temp_file.name

    def create_adapter(self, datafile, cfg=None, ftype=None):
        """Returns a BatchPluginAdapter instance with the specified input file, toolkit config file,
        and filetype."""
        return batchui_ctrl.BatchPluginAdapter(self.toolkit_class, datafile, cfg, ftype)

    def test_init_toolkit(self):
        """Verify initialization of a toolkit"""
        adapter = self.create_adapter(self.datafile)
        adapter.init_toolkit()
        self.assertTrue(hasattr(adapter, 'toolkit_instance'))
        self.assertEqual(type(adapter.toolkit_instance).__name__, self.toolkit_class)
        self.assertTrue(hasattr(adapter.toolkit_instance, 'config'))
        self.assertEqual(adapter.toolkit_instance.config['datafile'], self.datafile)

    def test_get_plugin_class(self):
        """Verify returning the correct plugin class based on name"""
        available_plugins = mainmodel.load_plugins()
        plugin_names = [plugin[0] for plugin in available_plugins]
        plugin_classes = [plugin[1] for plugin in available_plugins]
        for idx in range(len(plugin_names)):
            adapter = batchui_ctrl.BatchPluginAdapter(plugin_names[idx], self.datafile)
            retrieved_plugin_cls = adapter.get_plugin_class()
            retrieved_plugin_cls_inst = retrieved_plugin_cls()
            expected_plugin_cls_inst = plugin_classes[idx]()
            self.assertEqual(type(retrieved_plugin_cls_inst).__name__, type(expected_plugin_cls_inst).__name__)

    def test_read_data(self):
        """Verify returning NumPy data from a file"""
        sample_data_folder = os.path.join(pathfinder.app_path(), 'models', 'tests', 'support_files')
        # Verify Winspect 6/7 retrieval
        sample_winspect_file = os.path.join(sample_data_folder, 'sample_data.sdt')
        winspect_adapter = self.create_adapter(sample_winspect_file)
        winspect_adapter.read_data()
        returned_winspect_data = dataio.get_winspect_data(sample_winspect_file)
        for dataset in returned_winspect_data:
            expected_winspect_data = dataset.data
            retrieved_winspect_data = winspect_adapter.data[dataset.data_type + "0"]
            self.assertTrue(np.array_equal(expected_winspect_data, retrieved_winspect_data))
        # Verify bitmap retrieval
        sample_img_file = os.path.join(sample_data_folder, 'austin_sky320x240.jpg')
        expected_img_data = dataio.get_img_data(sample_img_file)
        img_adapter = self.create_adapter(sample_img_file)
        img_adapter.read_data()
        retrieved_img_data = img_adapter.data
        self.assertTrue(np.array_equal(expected_img_data, retrieved_img_data))
        # Verify UTWin retrieval
        sample_utwin_file = os.path.join(sample_data_folder, 'CScanData.csc')
        utwin_adapter = self.create_adapter(sample_utwin_file)
        expected_utwin_data = dataio.get_utwin_data(sample_utwin_file)
        utwin_adapter.read_data()
        retrieved_utwin_data = utwin_adapter.data
        for dataset in expected_utwin_data:
            self.assertTrue(np.array_equal(expected_utwin_data[dataset], retrieved_utwin_data[dataset]))

    def test_run(self):
        """Verify correctly executing NDIToolbox plugins"""
        available_plugins = mainmodel.load_plugins()
        plugin_names = [plugin[0] for plugin in available_plugins]
        plugin_classes = [plugin[1] for plugin in available_plugins]
        for idx in range(len(plugin_names)):
            adapter = batchui_ctrl.BatchPluginAdapter(plugin_names[idx], self.datafile)
            plugin_cls_inst = plugin_classes[idx]()
            plugin_cls_inst._data = dataio.get_data(self.datafile)
            plugin_cls_inst.run()
            expected_data = plugin_cls_inst._data
            adapter.run()
            returned_data = adapter.data
            self.assertTrue(np.array_equal(expected_data, returned_data))

if __name__ == "__main__":
    random.seed()
    unittest.main()
