"""test_mainmodel.py - tests the mainmodel module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import models.mainmodel as model
import models.abstractplugin as abstractplugin
import controllers.pathfinder as pathfinder
import numpy as np
import wx
import os.path
import os
import shutil
import unittest

class TestMainModel(unittest.TestCase):
    """Tests the main model"""

    def setUp(self):
        self.sample_data = np.ones(912)
        self.sample_data_basename = "sample.dat"
        self.sample_data_file = os.path.join(os.path.dirname(__file__),
                                             self.sample_data_basename)
        np.savetxt(self.sample_data_file, self.sample_data)
        self.mock_controller = ""
        self.model = model.MainModel(self.mock_controller)

    def test_get_data(self):
        """Verify get_data function returns a NumPy array"""
        import_parameters = {'delimiter':''}
        read_data = model.get_data(self.sample_data_file, **import_parameters)
        self.assertListEqual(self.sample_data.tolist(), read_data.tolist())

    def test_save_data(self):
        """Verify save_data function saves NumPy array to disk"""
        #save_data(data_fname, data, **export_params):
        sample_filename = "test_savedata.dat"
        sample_path = os.path.join(os.path.dirname(__file__), sample_filename)
        export_params = {'delim_char':':'}
        model.save_data(sample_path, self.sample_data, **export_params)
        self.assertTrue(os.path.exists(sample_path))
        read_data = np.loadtxt(sample_path, delimiter=export_params['delim_char'])
        self.assertListEqual(self.sample_data.tolist(), read_data.tolist())
        if os.path.exists(sample_path):
            os.remove(sample_path)

    def test_load_plugins(self):
        """Verify the main model loads available plugins"""
        plugin_list = model.load_plugins()
        for plugin in plugin_list:
            plugin_name = plugin[0]
            plugin_instance = plugin[1]
            self.assertTrue(issubclass(plugin_instance, abstractplugin.AbstractPlugin))

    def test_run_plugin(self):
        """Verify the main model can run a loaded plugin"""
        # The base A7117 source code comes with a normalize_plugin
        normalize_plugin_name = "NormalizePlugin"
        plugin_list = model.load_plugins()
        plugin_names = [plugin[0] for plugin in plugin_list]
        plugin_classes = [plugin[1] for plugin in plugin_list]
        # Ensure that the normalize plugin was found
        self.assertTrue(normalize_plugin_name in plugin_names)
        raw_data = np.array([-1.1, -2.2, 0, 3.3, 4.4, 1.19])
        expected_data = raw_data / np.max(raw_data)
        normalize_plugin = plugin_classes[plugin_names.index(normalize_plugin_name)]()
        normalize_plugin.data = raw_data
        normalize_plugin.run()
        generated_data = normalize_plugin.data
        self.assertListEqual(expected_data.tolist(), generated_data.tolist())

    def test_copy_data(self):
        """Verify copying of sample data file to data folder"""
        self.model.copy_data(self.sample_data_file)
        copied_data_file = os.path.join(pathfinder.data_path(),
                                        self.sample_data_basename)
        self.assertTrue(os.path.exists(copied_data_file))
        os.remove(copied_data_file)

    def test_remove_data(self):
        """Verify removal of a data file from the data folder"""
        self.model.copy_data(self.sample_data_file)
        copied_data_file = os.path.join(pathfinder.data_path(),
                                        self.sample_data_basename)
        self.assertTrue(os.path.exists(copied_data_file))
        self.model.remove_data(copied_data_file)
        self.assertFalse(os.path.exists(copied_data_file))

    def test_remove_thumbs(self):
        """Verify remove_thumbs method deletes all files in the thumbnail
        folder"""
        shutil.copy(__file__, pathfinder.thumbnails_path())
        self.assertTrue(len(os.listdir(pathfinder.thumbnails_path()))>0)
        self.model.remove_thumbs()
        self.assertListEqual(os.listdir(pathfinder.thumbnails_path()), [])

    def tearDown(self):
        if os.path.exists(self.sample_data_file):
            os.remove(self.sample_data_file)
