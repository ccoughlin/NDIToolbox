"""test_mainmodel.py - tests the mainmodel module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import models.mainmodel as model
import models.abstractplugin as abstractplugin
import controllers.pathfinder as pathfinder
import numpy as np
import os
import random
import shutil
import sys
import unittest

def deleted_user_path():
    """Utility function to delete empty folders in the user data folders,
    used to verify that MainModel will recreate missing folders as required.
    Returns a list of folders successfully deleted or None if no folders
    were deleted."""
    data_folders = [pathfinder.user_path(), pathfinder.data_path(), pathfinder.thumbnails_path(),
                    pathfinder.plugins_path()]
    deleted_folders = []
    for folder in data_folders:
        exists_and_empty = os.path.exists(folder) and os.listdir(folder) == []
        if exists_and_empty:
            try:
                os.rmdir(folder)
                deleted_folders.append(folder)
            except WindowsError: # folder in use (Explorer, cmd, etc.)
                pass
    if deleted_folders:
        return deleted_folders
    return None


class TestMainModel(unittest.TestCase):
    """Tests the main model"""

    def setUp(self):
        self.sample_data = np.array(self.random_data())
        self.sample_data_basename = "sample.dat"
        self.sample_data_file = os.path.join(os.path.dirname(__file__),
            self.sample_data_basename)
        np.savetxt(self.sample_data_file, self.sample_data)
        self.mock_controller = ""
        self.model = model.MainModel(self.mock_controller)

    def random_data(self):
        """Returns a list of random data"""
        return [random.uniform(-100, 100) for i in range(25)]

    @unittest.skipIf(deleted_user_path() is None,
        "User data folders in use")
    def test_check_user_path(self):
        """Verify main model creates the user data folders if not
        already in existence."""
        data_folders = [pathfinder.user_path(), pathfinder.data_path(),
                        pathfinder.thumbnails_path(),
                        pathfinder.plugins_path(), pathfinder.podmodels_path()]
        self.model.check_user_path()
        for folder in data_folders:
            self.assertTrue(os.path.exists(folder))

    def test_copy_system_plugins(self):
        """Verify main model copies system plugins to the user's
        plugins folder."""
        # Sample of system plugins to install
        system_plugins = ['medfilter_plugin.py', 'normalize_plugin.py', '__init__.py']
        # Try to remove them if already installed
        for plugin in system_plugins:
            installed_plugin = os.path.join(pathfinder.plugins_path(), plugin)
            if os.path.exists(installed_plugin):
                try:
                    os.remove(installed_plugin)
                except WindowsError: # file in use
                    pass
        self.model.copy_system_plugins()
        for plugin in system_plugins:
            installed_plugin = os.path.join(pathfinder.plugins_path(), plugin)
            self.assertTrue(os.path.exists(installed_plugin))

    def test_get_data(self):
        """Verify get_data function returns a NumPy array"""
        import_parameters = {'delimiter': ''}
        read_data = model.get_data(self.sample_data_file, **import_parameters)
        self.assertListEqual(self.sample_data.tolist(), read_data.tolist())

    def test_save_data(self):
        """Verify save_data function saves NumPy array to disk"""
        #save_data(data_fname, data, **export_params):
        sample_filename = "test_savedata.dat"
        sample_path = os.path.join(os.path.dirname(__file__), sample_filename)
        export_params = {'delim_char': ':'}
        model.save_data(sample_path, self.sample_data, **export_params)
        self.assertTrue(os.path.exists(sample_path))
        read_data = np.loadtxt(sample_path, delimiter=export_params['delim_char'])
        self.assertListEqual(self.sample_data.tolist(), read_data.tolist())
        if os.path.exists(sample_path):
            os.remove(sample_path)

    def test_import_dicom(self):
        """Verify import of DICOM / DICONDE data"""
        try:
            import dicom
            # Load the ASTM DICONDE example files,
            # save, then ensure the resulting arrays
            # are identical
            diconde_folder = os.path.join(os.path.dirname(__file__), 'support_files')
            for root, dirs, files in os.walk(diconde_folder):
                for fname in files:
                    dicom_data_file = os.path.join(root, fname)
                    basename, ext = os.path.splitext(dicom_data_file)
                    # Simple check to ensure we're looking at DICOM files
                    if ext.lower() == '.dcm':
                        dicom_data = dicom.read_file(dicom_data_file)
                        dicom_arr = dicom_data.pixel_array
                        try:
                            self.model.import_dicom(dicom_data_file)
                        except TypeError:
                            print(dicom_data_file)
                        dest_file = os.path.join(pathfinder.data_path(),
                            os.path.basename(dicom_data_file))
                        self.assertTrue(os.path.exists(dest_file))
                        read_data = np.loadtxt(dest_file, delimiter=',')
                        self.assertListEqual(dicom_arr.tolist(), read_data.tolist())
                        if os.path.exists(dest_file):
                            os.remove(dest_file)
        except ImportError:
            return

    def test_load_plugins(self):
        """Verify the main model loads available plugins"""
        plugin_list = model.load_plugins()
        for plugin in plugin_list:
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
        raw_data = np.array(self.random_data())
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
        self.assertTrue(len(os.listdir(pathfinder.thumbnails_path())) > 0)
        self.model.remove_thumbs()
        self.assertListEqual(os.listdir(pathfinder.thumbnails_path()), [])

    def test_get_windows_version(self):
        """Verify get_windows_version function returns correct version
        information."""
        if sys.platform == 'win32':
            win_ver = sys.getwindowsversion()
            major, minor = model.get_windows_version()
            self.assertEqual(win_ver.major, major)
            self.assertEqual(win_ver.minor, minor)
        else:
            self.assertIsNone(model.get_windows_version())

    def get_win_ver(self):
        """Returns the major, minor version of the Windows OS"""
        if sys.platform == 'win32':
            win_ver = sys.getwindowsversion()
            return win_ver.major, win_ver.minor
        return None

    def test_iswin7(self):
        """Verify is_win7 function returns True if running on Windows 7."""
        is_windows7 = False
        if sys.platform == 'win32':
            major, minor = self.get_win_ver()
            is_windows7 = major == 6 and minor == 1
        self.assertEqual(is_windows7, model.is_win7())

    def test_iswinvista(self):
        """Verify is_winvista function returns True if running on Windows Vista."""
        is_winvista = False
        if sys.platform == 'win32':
            major, minor = self.get_win_ver()
            is_winvista = major == 6 and minor == 0
        self.assertEqual(is_winvista, model.is_winvista())

    def test_iswinxp(self):
        """Verify is_winxp function returns True if running on Windows XP."""
        is_winxp = False
        if sys.platform == 'win32':
            major, minor = self.get_win_ver()
            is_winxp = major == 5 and minor == 1
        self.assertEqual(is_winxp, model.is_winxp())

    def test_iswinxp64(self):
        """Verify is_winxp64 function returns True if running on Windows XP x64."""
        is_winxp64 = False
        if sys.platform == 'win32':
            major, minor = self.get_win_ver()
            is_winxp = major == 5 and minor == 2
        self.assertEqual(is_winxp64, model.is_winxp64())

    def test_iswin2k(self):
        """Verify is_winxp function returns True if running on Windows 2000."""
        is_win2k = False
        if sys.platform == 'win32':
            major, minor = self.get_win_ver()
            is_win2k = major == 5 and minor == 0
        self.assertEqual(is_win2k, model.is_win2k())

    def tearDown(self):
        if os.path.exists(self.sample_data_file):
            os.remove(self.sample_data_file)

if __name__ == "__main__":
    random.seed()
    unittest.main()
