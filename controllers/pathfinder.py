'''pathfinder.py - specifies paths and common filenames'''
__author__ = 'Chris R. Coughlin'

import os.path
import sys

def app_path():
    '''Returns the base application path.'''
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        entry_point = sys.executable
    else:
        # TODO- implement after basic PyCharm testing completed
        #import __main__
        #if hasattr(__main__, "__file__"):
        #    entry_point = __main__.__file__
        #else:
        #    entry_point = sys.argv[0]
        entry_point = '/home/ccoughlin/PycharmProjects/Bane'
    #return os.path.dirname(entry_point)
    return entry_point

def resource_path():
    '''Returns the path to resources - home folder
    for icons, bitmaps, etc.'''
    return os.path.join(app_path(), 'resources')

def icon_path():
    '''Returns the path to application icons'''
    return os.path.join(resource_path(), 'icons')

def bitmap_path():
    '''Returns the path to application bitmaps'''
    return os.path.join(resource_path(), 'bitmaps')

def data_path():
    return os.path.join(app_path(), 'data')

def thumbnails_path():
    '''Returns the path to data thumbnails'''
    return os.path.join(app_path(), 'thumbnails')

  