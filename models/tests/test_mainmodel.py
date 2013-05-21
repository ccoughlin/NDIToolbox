"""test_mainmodel.py - tests the mainmodel module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import models.mainmodel as model
import models.dataio as dataio
import models.abstractplugin as abstractplugin
import models.config as config
import models.ultrasonicgate as ultrasonicgate
import controllers.pathfinder as pathfinder
from utils.skiptest import skipIfModuleNotInstalled
import h5py
import numpy as np
import logging
import multiprocessing
import os
import random
import shutil
import sys
import tempfile
import unittest


def deleted_user_path():
    """Utility function to delete empty folders in the user data folders,
    used to verify that MainModel will recreate missing folders as required.
    Returns a list of folders successfully deleted or None if no folders
    were deleted."""
    data_folders = [pathfinder.user_path(), pathfinder.data_path(), pathfinder.thumbnails_path(),
                    pathfinder.plugins_path(), pathfinder.colormaps_path()]
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


# Define a mock plugin to inspect results of calling plugin classes
class MockPlugin(abstractplugin.TRIPlugin):
    """Mock NDIToolbox plugin used to check plugin_wrapper"""

    def __init__(self, **kwargs):
        abstractplugin.TRIPlugin.__init__(self, **kwargs)
        self.config = {'a': 'b'}
        self._data = {'kwargs': kwargs}

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data['data'] = new_data

    def run(self):
        self._data['config'] = self.config

# A MockPlugin that raises an Exception on execution
class ExceptionPlugin(MockPlugin):
    """Raises an Exception on run() - used to verify
    exception Queue messaging"""

    def run(self):
        raise Exception("Wuh-oh.")


class TestMainModel(unittest.TestCase):
    """Tests the main model"""

    def setUp(self):
        self.sample_data = np.array(self.random_data())
        self.sample_data_basename = "sample.dat"
        self.sample_data_file = os.path.join(os.path.dirname(__file__),
                                             self.sample_data_basename)
        with h5py.File(self.sample_data_file, 'w') as fidout:
            fidout.create_dataset(self.sample_data_basename, data=self.sample_data)
        self.mock_controller = ""
        self.model = model.MainModel(self.mock_controller)
        cfg = config.Configure(pathfinder.config_path())
        self.original_loglevel = cfg.get_app_option("log level")

    def random_data(self):
        """Returns a list of random data"""
        return [random.uniform(-100, 100) for i in range(25)]

    @unittest.skipIf(deleted_user_path() is None,
                     "User data folders in use")
    def test_check_user_path(self):
        """Verify main model creates the user data folders if not
        already in existence."""
        self.check_user_path()

    def check_user_path(self):
        """Verify user data folders were created"""
        data_folders = [pathfinder.user_path(), pathfinder.data_path(),
                        pathfinder.thumbnails_path(), pathfinder.gates_path(),
                        pathfinder.plugins_path(), pathfinder.podmodels_path(),
                        pathfinder.colormaps_path(), pathfinder.batchoutput_path()]
        self.model.check_user_path()
        for folder in data_folders:
            self.assertTrue(os.path.exists(folder))

    def test_copy_system_files(self):
        """Verify main model copies dynamic modules to the specified
        folder."""
        test_module_folder = os.path.dirname(__file__)
        test_modules = []
        temp_dest_folder = tempfile.mkdtemp()
        module_files = os.listdir(test_module_folder)
        for module_file in module_files:
            module_name, module_extension = os.path.splitext(module_file)
            if module_name.startswith("test_") and\
               module_extension == os.extsep + "py":
                test_modules.append(module_file)
        self.model.copy_system_files(test_module_folder, temp_dest_folder)
        for module_file in test_modules:
            dest_module = os.path.join(temp_dest_folder, module_file)
            self.assertTrue(os.path.exists(dest_module))
        try:
            shutil.rmtree(temp_dest_folder)
        except WindowsError: # folder in use (Windows)
            pass

    def test_copy_system_plugins(self):
        """Verify main model copies system plugins to the user's
        plugins folder."""
        self.copy_system_plugins()

    def test_copy_system_gates(self):
        """Verify main model copies system ultrasonic gate plugins to the user's
        gates folder."""
        self.copy_system_gates()

    def test_copy_system_colormaps(self):
        """Verify main model copies colormaps to the user's colormaps folder."""
        self.copy_system_colormaps()

    def copy_system_plugins(self):
        """Verify system plugins are copied to the user's plugins folder"""
        # Sample of system plugins to install
        system_plugins = ['medfilter_plugin.py', 'normalize_plugin.py', '__init__.py']
        self.remove_system_files(system_plugins, pathfinder.plugins_path())
        self.model.copy_system_plugins()
        for plugin in system_plugins:
            installed_plugin = os.path.join(pathfinder.plugins_path(), plugin)
            self.assertTrue(os.path.exists(installed_plugin))

    def copy_system_gates(self):
        """Verify system ultrasonic gate plugins are copied to user's
        gates folder"""
        gate_plugins = ['predefined_gates.py', 'additional_gates.py', '__init__.py']
        self.remove_system_files(gate_plugins, pathfinder.gates_path())
        self.model.copy_system_gates()
        for gate in gate_plugins:
            installed_gate = os.path.join(pathfinder.gates_path(), gate)
            self.assertTrue(os.path.exists(installed_gate))

    def copy_system_colormaps(self):
        """Verify system colormaps are copied to user's folder"""
        colormaps_folder = os.path.join(pathfinder.app_path(), 'colormaps')
        colormaps = os.listdir(colormaps_folder)
        self.remove_system_files(colormaps, pathfinder.colormaps_path())
        self.model.copy_system_colormaps()
        for cmap in colormaps:
            installed_cmap = os.path.join(pathfinder.colormaps_path(), cmap)
            self.assertTrue(os.path.exists(installed_cmap))

    def remove_system_files(self, file_list, dest):
        """Attempts to remove every file in file_list found in dest folder.
        Used to verify copying system files to user's local data folder."""
        for each_file in file_list:
            dest_path = os.path.join(dest, each_file)
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except WindowsError: # file in use (Windows)
                    pass


    def test_migrate_user_path(self):
        """Verify migration of the user's data folder"""
        current_user_path = pathfinder.user_path()
        temp_user_path = tempfile.mkdtemp()
        self.model.migrate_user_path(temp_user_path)
        self.check_user_path()
        self.copy_system_plugins()
        self.model.migrate_user_path(current_user_path)
        try:
            shutil.rmtree(temp_user_path)
        except WindowsError: # folder in use
            pass

    def test_load_dynamic_modules(self):
        """Verify the main model's dynamic module loading"""
        plugin_list = model.load_dynamic_modules(pathfinder.plugins_path(), abstractplugin.AbstractPlugin)
        for plugin in plugin_list:
            plugin_instance = plugin[1]
            self.assertTrue(issubclass(plugin_instance, abstractplugin.AbstractPlugin))

    def test_load_plugins(self):
        """Verify the main model loads available plugins"""
        plugin_list = model.load_plugins()
        for plugin in plugin_list:
            plugin_instance = plugin[1]
            self.assertTrue(issubclass(plugin_instance, abstractplugin.AbstractPlugin))

    def test_load_gates(self):
        """Verify the main model loads available gates"""
        gate_list = model.load_gates()
        for gate in gate_list:
            gate_instance = gate[1]
            self.assertTrue(issubclass(gate_instance, ultrasonicgate.UltrasonicGate))


    def test_plugin_wrapper(self):
        """Verify the plugin_wrapper function properly configures and runs a plugin"""
        plugin_queue = multiprocessing.Queue()
        plugin_exception_queue = multiprocessing.Queue()
        plugin_data = np.array(self.random_data())
        plugin_cfg = {'a': 'c'}
        kwargs = {'name': 'Mock Plugin', 'description': 'Mock plugin used to test plugin_wrapper'}
        model.plugin_wrapper(plugin_exception_queue, MockPlugin, plugin_data, plugin_queue, plugin_cfg,
                             **kwargs)
        returned_data = plugin_queue.get()
        self.assertTrue(isinstance(returned_data, dict))
        self.assertDictEqual(returned_data['config'], plugin_cfg)
        self.assertDictEqual(returned_data['kwargs'], kwargs)
        self.assertTrue(np.array_equal(returned_data['data'], plugin_data))

    def test_plugin_wrapper_exceptions(self):
        """Verify the plugin_wrapper function properly returns Exception info"""
        plugin_queue = multiprocessing.Queue()
        plugin_exception_queue = multiprocessing.Queue()
        plugin_data = np.array(self.random_data())
        model.plugin_wrapper(exception_queue=plugin_exception_queue,
                             plugin_cls=ExceptionPlugin,
                             plugin_data=plugin_data,
                             plugin_queue=plugin_queue)
        exc_type, exc = plugin_exception_queue.get(block=True)
        self.assertTrue(isinstance(exc, Exception))

    @skipIfModuleNotInstalled("tcunittest")
    def test_run_plugin(self):
        """Verify the main model can run a loaded plugin"""
        plugin_data = np.array(self.random_data())
        plugin_config = {'pi': 3.141592654}
        plugin_cls = self.get_normalize_plugin()
        plugin_process, plugin_queue, exception_queue = model.run_plugin(plugin_cls,
                                                                         data=plugin_data, config=plugin_config)
        self.assertTrue(isinstance(plugin_process, multiprocessing.Process))
        returned_data = plugin_queue.get()
        expected_data = plugin_data / np.max(plugin_data)
        self.assertTrue(np.array_equal(expected_data, returned_data))

    @skipIfModuleNotInstalled("tcunittest")
    def test_run_plugin_exceptions(self):
        """Verify run_plugin returns exception messages in Queue"""
        plugin_data = np.zeros(5) # Use division by zero exception in NormalizePlugin
        plugin_config = {'pi': 3.141592654}
        plugin_cls = self.get_normalize_plugin()
        plugin_process, plugin_queue, exception_queue = model.run_plugin(plugin_cls,
                                                                         data=plugin_data, config=plugin_config)
        exc_type, exc = exception_queue.get(block=True)
        self.assertTrue(isinstance(exc, Exception))

    def get_normalize_plugin(self):
        """Returns NDIToolbox's NormalizePlugin plugin"""
        normalize_plugin_name = "NormalizePlugin"
        plugin_list = model.load_plugins()
        plugin_names = [plugin[0] for plugin in plugin_list]
        plugin_classes = [plugin[1] for plugin in plugin_list]
        # Ensure that the normalize plugin was found
        self.assertTrue(normalize_plugin_name in plugin_names)
        return plugin_classes[plugin_names.index(normalize_plugin_name)]

    def test_get_config(self):
        """Verify returning the application's configuration"""
        expected_configuration = config.Configure(pathfinder.config_path()).config
        expected_configuration.read(pathfinder.config_path())
        returned_configuration = model.get_config().config
        returned_configuration.read(pathfinder.config_path())
        for section in expected_configuration.sections():
            self.assertListEqual(expected_configuration.items(section), returned_configuration.items(section))

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

    def test_get_preview_state(self):
        """Verify returning the current setting for displaying plot thumbnails"""
        cfg = config.Configure(pathfinder.config_path())
        preview_state = cfg.get_app_option_boolean("Enable Preview")
        self.assertEqual(preview_state, self.model.get_preview_state())

    def test_set_preview_state(self):
        """Verify setting the current setting for displaying plot thumbnails"""
        cfg = config.Configure(pathfinder.config_path())
        original_preview_state = cfg.get_app_option_boolean("Enable Preview")
        new_preview_state = not original_preview_state
        self.assertEqual(original_preview_state, self.model.get_preview_state())
        self.model.set_preview_state(new_preview_state)
        self.assertEqual(new_preview_state, self.model.get_preview_state())
        self.model.set_preview_state(original_preview_state)

    def test_get_coords(self):
        """Verify returning the UL corner of the main app window set in config"""
        cfg = config.Configure(pathfinder.config_path())
        str_coords = cfg.get_app_option_list("Coordinates")
        expected_coords = (0, 0)
        if str_coords is not None:
            expected_coords = [int(coord) for coord in str_coords]
        self.assertListEqual(expected_coords, self.model.get_coords())

    def test_set_coords(self):
        """Verify setting the UL corner of the main app window in config"""
        cfg = config.Configure(pathfinder.config_path())
        str_coords = cfg.get_app_option_list("Coordinates")
        original_coords = (0, 0)
        if str_coords is not None:
            original_coords = [int(coord) for coord in str_coords]
        self.assertListEqual(original_coords, self.model.get_coords())
        new_coords_int = [3, 5]
        self.model.set_coords(new_coords_int)
        self.assertListEqual(new_coords_int, self.model.get_coords())
        new_coords_str = ["9", "-1"]
        self.model.set_coords(new_coords_str)
        self.assertListEqual([int(coord) for coord in new_coords_str], self.model.get_coords())
        self.model.set_coords(original_coords)

    def test_get_size(self):
        """Verify returning the size of the main app window set in config"""
        cfg = config.Configure(pathfinder.config_path())
        str_win_size = cfg.get_app_option_list("Window Size")
        expected_win_size = [300, 600]
        if str_win_size is not None:
            expected_win_size = [int(dimsize) for dimsize in str_win_size]
        self.assertListEqual(expected_win_size, self.model.get_window_size())

    def test_set_size(self):
        """Verify setting the size of the main app window in config"""
        cfg = config.Configure(pathfinder.config_path())
        str_win_size = cfg.get_app_option_list("Window Size")
        original_win_size = [300, 600]
        if str_win_size is not None:
            original_win_size = [int(dimsize) for dimsize in str_win_size]
        self.assertListEqual(original_win_size, self.model.get_window_size())
        new_win_size = [800, 1024]
        self.model.set_window_size(new_win_size)
        self.assertListEqual(new_win_size, self.model.get_window_size())
        self.model.set_window_size(original_win_size)

    def test_get_loglevel(self):
        """Verify returning the log level from config"""
        cfg = config.Configure(pathfinder.config_path())
        log_level = cfg.get_app_option("log level")
        available_log_levels = {'debug': logging.DEBUG,
                                'info': logging.INFO,
                                'warning': logging.WARNING,
                                'error': logging.ERROR,
                                'critical': logging.CRITICAL}
        log_level = available_log_levels.get(log_level, logging.WARNING)
        self.assertEqual(log_level, model.get_loglevel())

    def test_set_loglevel(self):
        """Verify setting the log level in config"""
        cfg = config.Configure(pathfinder.config_path())
        log_levels = ['debug', 'info', 'warning', 'error', 'critical', None, 'abc']
        acceptable_log_levels = {'debug': logging.DEBUG,
                                 'info': logging.INFO,
                                 'warning': logging.WARNING,
                                 'error': logging.ERROR,
                                 'critical': logging.CRITICAL}
        for level in log_levels:
            model.set_loglevel(level)
            if level in acceptable_log_levels:
                self.assertEqual(acceptable_log_levels[level], model.get_loglevel())

    def test_get_loglevels(self):
        """Verify returning a list of available log levels"""
        available_log_levels = {'debug': logging.DEBUG,
                                'info': logging.INFO,
                                'warning': logging.WARNING,
                                'error': logging.ERROR,
                                'critical': logging.CRITICAL}
        self.assertDictEqual(available_log_levels, model.available_log_levels)

    def test_get_logger(self):
        """Verify returning a logger instance"""
        logger = model.get_logger(__name__)
        self.assertTrue(isinstance(logger, logging.Logger))
        expected_logger = logging.getLogger(name='.'.join(['nditoolbox', __name__]))
        self.assertEqual(expected_logger.name, logger.name)
        acceptable_log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        for level in acceptable_log_levels:
            self.assertEqual(expected_logger.isEnabledFor(level), logger.isEnabledFor(level))

    def test_clear_log(self):
        """Verify deleting the log file"""
        log_file = pathfinder.log_path()
        if os.path.exists(log_file):
            try:
                model.clear_log()
                self.assertFalse(os.path.exists(log_file))
            except WindowsError: # file in use (Windows)
                pass

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
            is_winxp64 = major == 5 and minor == 2
        self.assertEqual(is_winxp64, model.is_winxp64())

    def test_iswin2k(self):
        """Verify is_winxp function returns True if running on Windows 2000."""
        is_win2k = False
        if sys.platform == 'win32':
            major, minor = self.get_win_ver()
            is_win2k = major == 5 and minor == 0
        self.assertEqual(is_win2k, model.is_win2k())

    def test_get_data_info(self):
        """Verify get_data_info returns info about a data file"""
        file_size = int(os.stat(self.sample_data_file).st_size)
        data = dataio.get_data(self.sample_data_file)
        data_info = self.model.get_data_info(self.sample_data_file)
        ndim = data.ndim
        shape = data.shape
        numpoints = data.size
        dtype = str(data.dtype)
        self.assertEqual(file_size, data_info['filesize'])
        self.assertEqual(ndim, data_info['ndim'])
        self.assertEqual(shape, data_info['shape'])
        self.assertEqual(numpoints, data_info['numpoints'])
        self.assertEqual(dtype, data_info['dtype'])

    def tearDown(self):
        try:
            if os.path.exists(self.sample_data_file + ".hdf5"):
                os.remove(self.sample_data_file + ".hdf5")
            if os.path.exists(self.sample_data_file):
                os.remove(self.sample_data_file)
        except WindowsError: # file in use
            pass
        model.set_loglevel(self.original_loglevel)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    random.seed()
    unittest.main()
