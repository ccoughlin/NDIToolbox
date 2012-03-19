"""pathfinder.py - specifies paths and common filenames"""
__author__ = 'Chris R. Coughlin'

from models import config
import os.path
import sys

def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        entry_point = sys.executable
    else:
        import controllers

        entry_point = os.path.dirname(controllers.__file__)
    return os.path.dirname(entry_point)


def user_path():
    """Returns the path for storing user data.  If not already set,
    returns user's home directory/a7117 and sets the default in the
    config file."""
    _config = config.Configure(config_path())
    upath_key = "User Path"
    if _config.has_app_option(upath_key):
        return _config.get_app_option(upath_key)
    else:
        default_upath = os.path.normcase(os.path.join(os.path.expanduser('~'), 'a7117'))
        _config.set_app_option({upath_key: default_upath})
        return default_upath


def resource_path():
    """Returns the path to resources - home folder
    for icons, bitmaps, etc."""
    return os.path.join(app_path(), 'resources')


def icons_path():
    """Returns the path to application icons"""
    return os.path.join(resource_path(), 'icons')


def icon_path():
    """Returns the path to the application's default
    PNG icon"""
    return os.path.join(icons_path(), 'a7117_64.png')


def winicon_path():
    """Returns the path to the application's default
    .ICO icon"""
    return os.path.join(icons_path(), 'a7117_64.ico')


def bitmap_path():
    """Returns the path to application bitmaps"""
    return os.path.join(resource_path(), 'bitmaps')


def data_path():
    """Returns the path to data files"""
    return os.path.join(user_path(), 'data')


def thumbnails_path():
    """Returns the path to data thumbnails"""
    return os.path.join(user_path(), 'thumbnails')


def plugins_path():
    """Returns the path to plugins"""
    return os.path.join(user_path(), 'plugins')


def config_path():
    """Returns the path to the configuration file"""
    return os.path.expanduser("~/a7117.cfg")


def podmodels_path():
    """Returns the path to POD Toolkit models"""
    return os.path.join(user_path(), "podmodels")