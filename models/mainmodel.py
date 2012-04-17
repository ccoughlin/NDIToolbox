""" mainmodel.py - primary model for the project

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
from models import abstractplugin
from models import config
import dicom
import numpy as np
import h5py
import imp
import inspect
import os
import shutil
import sys

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


def load_plugins():
    """Searches the plugins folder and imports all valid plugins,
    returning a list of the plugins successfully imported as tuples:
    first element is the plugin name (e.g. MyPlugin), second element is
    the class of the plugin."""
    plugins_folder = pathfinder.plugins_path()
    plugins = []
    if not plugins_folder in sys.path:
        sys.path.append(plugins_folder)
    for root, dir, files in os.walk(pathfinder.plugins_path()):
        for module_file in files:
            module_name, module_extension = os.path.splitext(module_file)
            if module_extension == os.extsep + "py":
                try:
                    module_hdl, path_name, description = imp.find_module(module_name)
                    plugin_module = imp.load_module(module_name, module_hdl, path_name,
                                                    description)
                    plugin_classes = inspect.getmembers(plugin_module, inspect.isclass)
                    for plugin_class in plugin_classes:
                        if issubclass(plugin_class[1], abstractplugin.AbstractPlugin):
                            # Load only those plugins defined in the current module
                            # (i.e. don't instantiate any parent plugins)
                            if plugin_class[1].__module__ == module_name:
                                #plugin = plugin_class[1]()
                                plugins.append(plugin_class)
                finally:
                    if module_hdl:
                        module_hdl.close()
    return plugins


def get_config():
    """Returns a Configure instance pointing to the application's
    default configuration file."""
    return config.Configure(pathfinder.config_path())


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
        for fldr in (user_folder, data_folder, thumbnail_folder, plugins_folder, podmodels_folder):
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
        """Copies plugins that ship with the application
        to the user's plugins folder."""
        system_plugins_folder = os.path.join(pathfinder.app_path(), 'plugins')
        for root, dir, files in os.walk(system_plugins_folder):
            for module_file in files:
                module_name, module_extension = os.path.splitext(module_file)
                if module_extension == os.extsep + "py":
                    installed_plugin = os.path.join(pathfinder.plugins_path(), module_file)
                    if not os.path.exists(installed_plugin):
                        system_plugin = os.path.join(system_plugins_folder, module_file)
                        shutil.copy(system_plugin, pathfinder.plugins_path())

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
        di_struct = dicom.read_file(data_file)
        export_parameters = {'delimiter': ','}
        di_fname = os.path.join(pathfinder.data_path(),
                                os.path.basename(data_file))
        # TODO - implement support for 3D arrays
        # when data format is finalized
        if di_struct.pixel_array.ndim > 2:
            return
        save_data(di_fname, di_struct.pixel_array)

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
        coords = (0, 0)
        if str_coords is not None:
            coords = [int(coord) for coord in config.get_app_option_list("Coordinates")]
        return coords