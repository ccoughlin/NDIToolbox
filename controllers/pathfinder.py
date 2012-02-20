"""pathfinder.py - specifies paths and common filenames"""
__author__ = 'Chris R. Coughlin'

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


def bitmap_path():
    """Returns the path to application bitmaps"""
    return os.path.join(resource_path(), 'bitmaps')


def data_path():
    return os.path.join(app_path(), 'data')


def thumbnails_path():
    """Returns the path to data thumbnails"""
    return os.path.join(app_path(), 'thumbnails')


def plugins_path():
    """Returns the path to plugins"""
    return os.path.join(app_path(), 'plugins')


def config_path():
    """Returns the path to the configuration file"""
    return os.path.expanduser("~/a7117.cfg")