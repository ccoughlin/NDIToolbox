"""pathfinder.py - specifies paths and common filenames"""
__author__ = 'Chris R. Coughlin'

from models import config
import os.path
import sys

def normalized(path_fn):
    """Decorator to normalize (os.path.normcase) paths"""

    def normalize():
        return os.path.normcase(path_fn())

    return normalize


@normalized
def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        entry_point = sys.executable
    else:
        import controllers

        entry_point = os.path.dirname(controllers.__file__)
    return os.path.dirname(entry_point)


@normalized
def user_path():
    """Returns the path for storing user data.  If not already set,
    returns user's home directory/nditoolbox and sets the default in the
    config file."""
    _config = config.Configure(config_path())
    upath_key = "User Path"
    if _config.has_app_option(upath_key):
        return _config.get_app_option(upath_key)
    else:
        default_upath = os.path.normcase(os.path.join(os.path.expanduser('~'), 'nditoolbox'))
        _config.set_app_option({upath_key: default_upath})
        return default_upath


@normalized
def docs_path():
    """Returns the path to the HTML documentation."""
    return os.path.join(app_path(), 'docs')


@normalized
def resource_path():
    """Returns the path to resources - home folder
    for icons, bitmaps, etc."""
    return os.path.join(app_path(), 'resources')


@normalized
def icons_path():
    """Returns the path to application icons"""
    return os.path.join(resource_path(), 'icons')


@normalized
def icon_path():
    """Returns the path to the application's default
    PNG icon"""
    return os.path.join(icons_path(), 'a7117_64.png')


@normalized
def winicon_path():
    """Returns the path to the application's default
    .ICO icon"""
    return os.path.join(icons_path(), 'a7117_64.ico')


@normalized
def bitmap_path():
    """Returns the path to application bitmaps"""
    return os.path.join(resource_path(), 'bitmaps')


@normalized
def textfiles_path():
    """Returns the path to application textfiles"""
    return os.path.join(resource_path(), 'textfiles')


@normalized
def data_path():
    """Returns the path to data files"""
    return os.path.join(user_path(), 'data')


@normalized
def thumbnails_path():
    """Returns the path to data thumbnails"""
    return os.path.join(user_path(), 'thumbnails')


@normalized
def plugins_path():
    """Returns the path to plugins"""
    return os.path.join(user_path(), 'plugins')


@normalized
def config_path():
    """Returns the path to the configuration file"""
    return os.path.expanduser("~/nditoolbox.cfg")


@normalized
def log_path():
    """Returns the path to the log file.  If not already set,
    sets to user's home directory/nditoolbox.log and sets the default in the config file."""
    _config = config.Configure(config_path())
    logpath_key = "Log File"
    if _config.has_app_option(logpath_key):
        return _config.get_app_option(logpath_key)
    else:
        default_logpath = os.path.normcase(os.path.join(os.path.expanduser('~'), 'nditoolbox.log'))
        _config.set_app_option({logpath_key: default_logpath})
        return default_logpath


@normalized
def podmodels_path():
    """Returns the path to POD Toolkit models"""
    return os.path.join(user_path(), "podmodels")


@normalized
def gates_path():
    """Returns the path to ultrasonic gates"""
    return os.path.join(user_path(), "gates")