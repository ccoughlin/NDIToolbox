""" mainmodel.py - primary model for the project

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
from models import abstractplugin
from models import config
import numpy as np
import scipy.misc
import h5py
import imp
import inspect
import logging
import logging.handlers
import multiprocessing
import os
import shutil
import sys

def get_config():
    """Returns a Configure instance pointing to the application's
    default configuration file."""
    return config.Configure(pathfinder.config_path())

# Define the available log severity levels
available_log_levels = {'debug': logging.DEBUG,
                        'info': logging.INFO,
                        'warning': logging.WARNING,
                        'error': logging.ERROR,
                        'critical': logging.CRITICAL}

def get_loglevel():
    """Returns the current logging severity level set in config
    (defaults to logging.WARNING if not specified)"""
    config = get_config()
    log_level = config.get_app_option("log level")
    return available_log_levels.get(log_level, logging.WARNING)

def set_loglevel(level):
    """Sets the application's logging severity level in configuration
    (defaults to logging.WARNING)"""
    config = get_config()
    acceptable_log_levels = available_log_levels.keys()
    if level is not None and level in acceptable_log_levels:
        config.set_app_option({'log level': level})

def get_logger(module_name):
    """Returns a Logger instance for the specified module_name"""
    logger = logging.getLogger('.'.join(['nditoolbox', module_name]))
    logger.setLevel(get_loglevel())
    # Default to starting a new log every 7 days, keeping a copy of the last 7 days' events
    log_handler = logging.handlers.TimedRotatingFileHandler(pathfinder.log_path(), when='D', interval=7, backupCount=1)
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    return logger

def clear_log():
    """Deletes the current log file.  Backup log files (if any) are untouched.
    On Windows, raises WindowsError if file is in use."""
    log_file = pathfinder.log_path()
    if os.path.exists(log_file):
        os.remove(log_file)

module_logger = get_logger(__name__)

def get_data(data_fname):
    with h5py.File(data_fname, 'r') as fidin:
        root, ext = os.path.splitext(os.path.basename(data_fname))
        for key in fidin.keys():
            if key.startswith(root):
                return fidin[key][...]


def save_data(data_fname, data):
    """Saves the data to the HDF5 file data_fname"""
    root, ext = os.path.splitext(data_fname)
    output_filename = data_fname
    hdf5_ext = '.hdf5'
    if ext.lower() != hdf5_ext:
        output_filename += hdf5_ext
    with h5py.File(output_filename, 'w') as fidout:
        fidout.create_dataset(os.path.basename(data_fname), data=data)


def load_dynamic_modules(module_path, module_class):
    """Dynamically imports the modules in module_path and searches
    the modules for subclasses of module_class.  Returns a list of tuples
    (plugin_name, plugin_class)."""
    if not module_path in sys.path:
        module_logger.info("Adding {0} to sys.path".format(module_path))
        sys.path.append(module_path)
    dynamic_modules = []
    for root, dirs, files in os.walk(module_path):
        for found_file in files:
            file_name, file_extension = os.path.splitext(found_file)
            if file_extension == os.extsep + "py":
                try:
                    module_hdl, path_name, description = imp.find_module(file_name)
                    dyn_module = imp.load_module(file_name, module_hdl, path_name, description)
                    dyn_module_classes = inspect.getmembers(dyn_module, inspect.isclass)
                    for dyn_module_class in dyn_module_classes:
                        if issubclass(dyn_module_class[1], module_class):
                            # Load only those plugins defined in the current module
                            # (i.e. don't instantiate any parent plugins)
                            if dyn_module_class[1].__module__ == file_name:
                                module_logger.info("Module {0} successfully imported.".format(dyn_module_class))
                                dynamic_modules.append(dyn_module_class)
                except ImportError as err: # imp.load_module failed to load module
                    module_logger.error("load_module failed: {0}".format(err))
                    raise err
                except Exception as err: # unknown error
                    module_logger.error("Unable to load module: {0}".format(err))
                    raise err
                finally:
                    if module_hdl:
                        module_hdl.close()
    return dynamic_modules


def load_plugins():
    """Searches the plugins folder and imports all valid plugins,
    returning a list of the plugins successfully imported as tuples:
    first element is the plugin name (e.g. MyPlugin), second element is
    the class of the plugin."""
    return load_dynamic_modules(pathfinder.plugins_path(), abstractplugin.AbstractPlugin)


def load_gates():
    """Searches the plugins folder and imports all valid ultrasonic gate plugins,
    returning a list of the plugins successfully imported as tuples:
    first element is the plugin name (e.g. MyGate), second element is
    the class of the plugin."""
    return load_dynamic_modules(pathfinder.gates_path(), abstractplugin.AbstractPlugin)


def plugin_wrapper(exception_queue, plugin_cls, plugin_data, plugin_queue, plugin_cfg=None, **kwargs):
    """multiprocessing wrapper function, used to execute
    plugin run() method in separate process.  plugin_cls is the Plugin class
    to instantiate, plugin_data is the data to run the plugin on, and
    plugin_queue is the Queue instance the function should return the
    results in back to the caller.  If plugin_cfg is not None, it is
    supplied to the Plugin instance as its config dict.
    """

    plugin_instance = plugin_cls(**kwargs)
    plugin_instance.data = plugin_data
    if plugin_cfg is not None:
        plugin_instance.config = plugin_cfg
    try:
        # Instruct NumPy to raise all warnings (division by zero, etc.)
        # to Exceptions to pass to exception queue
        np.seterr(all='raise')
        plugin_instance.run()
        plugin_queue.put(plugin_instance.data)
    except Exception as err:
        # Pass a message to the parent process with the Exception information
        module_logger.error("Error running plugin: {0}".format(err))
        exception_queue.put(sys.exc_info()[:2])


def run_plugin(plugin_cls, data=None, config=None, **kwargs):
    """Runs the plugin plugin_cls"""
    plugin_queue = multiprocessing.Queue()
    plugin_exception_queue = multiprocessing.Queue()
    plugin_process = multiprocessing.Process(target=plugin_wrapper,
                                             args=(plugin_exception_queue, plugin_cls, data, plugin_queue, config),
                                             kwargs=kwargs)
    plugin_process.daemon = True
    plugin_process.start()
    return plugin_process, plugin_queue, plugin_exception_queue

def get_windows_version():
    """Returns the major, minor version of the
    Windows OS, or None if not on Windows."""
    if sys.platform == 'win32':
        win_ver = sys.getwindowsversion()
        return win_ver.major, win_ver.minor
    return None


def is_win7():
    """Returns True if the host OS appears
    to be Windows 7 or Windows Server 2008 R2."""
    retval = False
    if sys.platform == 'win32':
        major, minor = get_windows_version()
        if major == 6 and minor == 1:
            retval = True
    return retval


def is_winvista():
    """Returns True if the host OS appears
    to be Windows Vista or Windows Server 2008."""
    retval = False
    if sys.platform == 'win32':
        major, minor = get_windows_version()
        if major == 6 and minor == 0:
            retval = True
    return retval


def is_winxp():
    """Returns True if the host OS appears
    to be Windows XP."""
    retval = False
    if sys.platform == 'win32':
        major, minor = get_windows_version()
        if major == 5 and minor == 1:
            retval = True
    return retval


def is_winxp64():
    """Returns True if the host OS appears
    to be Windows XP Pro x64."""
    retval = False
    if sys.platform == 'win32':
        major, minor = get_windows_version()
        if major == 5 and minor == 2:
            retval = True
    return retval


def is_win2k():
    """Returns True if the host OS appears
    to be Windows 2000."""
    retval = False
    if sys.platform == 'win32':
        major, minor = get_windows_version()
        if major == 5 and minor == 0:
            retval = True
    return retval

class MainModel(object):
    """Model for the main user interface"""

    def __init__(self, controller):
        self.controller = controller

    def check_user_path(self):
        """Verify that user data folders exist.  Creates
        any missing folders."""
        user_folder = pathfinder.user_path()
        data_folder = pathfinder.data_path()
        thumbnail_folder = pathfinder.thumbnails_path()
        plugins_folder = pathfinder.plugins_path()
        podmodels_folder = pathfinder.podmodels_path()
        gates_folder = pathfinder.gates_path()
        for fldr in (user_folder, data_folder, thumbnail_folder, plugins_folder, podmodels_folder, gates_folder):
            if not os.path.exists(fldr):
                os.makedirs(fldr)

    def migrate_user_path(self, new_user_path):
        """Sets the default user path to new_user_path, creating
        the path if necessary and copying system plugins.
        """
        config = get_config()
        config.set_app_option({"User Path": os.path.normcase(new_user_path)})
        self.check_user_path()
        self.copy_system_plugins()

    def copy_system_plugins(self):
        """Copies plugins that ship with the application to the user's plugins folder."""
        system_plugins_folder = os.path.join(pathfinder.app_path(), 'plugins')
        self.copy_system_files(system_plugins_folder, pathfinder.plugins_path())

    def copy_system_gates(self):
        """Copies ultrasonic gate plugins that ship with the application to the user's gates folder."""
        system_gates_folder = os.path.join(pathfinder.app_path(), 'gates')
        self.copy_system_files(system_gates_folder, pathfinder.gates_path())

    def copy_system_files(self, src_folder, dest_folder):
        """Copies the Python (.py) files in src_folder to dest_folder.
        Used to install local user-editable copies of plugins, POD Models,
        and ultrasonic gates."""
        files = os.listdir(src_folder)
        for module_file in files:
            module_name, module_extension = os.path.splitext(module_file)
            if module_extension == os.extsep + "py":
                installed_module = os.path.join(dest_folder, module_file)
                if not os.path.exists(installed_module):
                    src_module = os.path.join(src_folder, module_file)
                    shutil.copy(src_module, dest_folder)

    def copy_data(self, data_file):
        """Adds the specified data file to the data folder"""
        shutil.copy(data_file, pathfinder.data_path())

    def export_txt(self, dest, src, **export_params):
        """Exports the NumPy array data to the text file data_fname,
        using the supplied export parameters."""
        delim_char = export_params.get('delimiter', None)
        newline = export_params.get('newline', '\n')
        fmt = export_params.get('format', '%f')
        data = get_data(src)
        np.savetxt(dest, data, fmt=fmt, delimiter=delim_char, newline=newline)

    def import_txt(self, data_fname, **import_params):
        """Loads the data from an ASCII-delimited text file, and copies
        the data to a new HDF5 file in the data folder"""
        comment_char = import_params.get('commentchar', '#')
        delim_char = import_params.get('delimiter', None)
        header_lines = import_params.get('skipheader', 0)
        footer_lines = import_params.get('skipfooter', 0)
        cols_to_read = import_params.get('usecols', None)
        transpose_data = import_params.get('transpose', False)
        data = np.genfromtxt(data_fname, comments=comment_char, delimiter=delim_char,
                             skip_header=header_lines, skip_footer=footer_lines, usecols=cols_to_read,
                             unpack=transpose_data)
        output_fname = os.path.join(pathfinder.data_path(), os.path.basename(data_fname))
        save_data(output_fname, data)

    def import_dicom(self, data_file):
        """Imports a DICOM/DICONDE pixel map"""
        """Imports a DICOM/DICONDE pixel map"""
        try:
            import dicom

            di_struct = dicom.read_file(data_file)
            di_fname = os.path.join(pathfinder.data_path(),
                                    os.path.basename(data_file))
            save_data(di_fname, di_struct.pixel_array)
        except ImportError as err: # pydicom not installed
            module_logger.error("pydicom not found: {0}".format(err))
            raise ImportError("pydicom module not installed.")

    def import_img(self, data_file, flatten=True):
        """Imports an image file, by default flattening
        the image to a single layer grayscale."""
        img_arr = scipy.misc.imread(data_file, flatten)
        img_fname = os.path.join(pathfinder.data_path(), os.path.basename(data_file))
        save_data(img_fname, img_arr)

    def remove_data(self, data_file):
        """Removes specified file from the device"""
        os.remove(data_file)

    def remove_thumbs(self):
        """Removes all the thumnbail plots"""
        thumbnail_path = pathfinder.thumbnails_path()
        for thumbnail in os.listdir(thumbnail_path):
            os.remove(os.path.join(thumbnail_path, thumbnail))

    def set_preview_state(self, preview_state):
        """Writes an entry into the configuration file
        indicating whether thumbnails should be enabled
        or disabled."""
        config = get_config()
        config.set_app_option({"Enable Preview": preview_state})

    def get_preview_state(self):
        """Returns the current setting for whether
        thumbnail previews are enabled or disabled"""
        config = get_config()
        return config.get_app_option_boolean("Enable Preview")

    def set_coords(self, coordinate_list):
        """Writes the specified coordinate list
        to the default configuration file."""
        config = get_config()
        config.set_app_option({"Coordinates": coordinate_list})

    def get_coords(self):
        """Returns the default (x, y)
        coordinates from the configuration file."""
        config = get_config()
        str_coords = config.get_app_option_list("Coordinates")
        coords = [0, 0]
        if str_coords is not None:
            coords = [int(coord) for coord in config.get_app_option_list("Coordinates")]
        return coords
