"""uimodel.py - model for the user interface

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'ccoughlin'

from controllers import pathfinder
import numpy as np
from matplotlib import colors
from matplotlib import cm
import json
import os
import os.path

class ColormapCreatorModel(object):
    """Model for the ColormapCreator user interface"""

    def __init__(self, controller):
        self.controller = controller

    def get_cmap(self, cmap_name, usercmaps_folder=pathfinder.colormaps_path()):
        """Returns a matplotlib colormap of specified name cmap_name, searching the predefined
        matplotlib colormaps first.  If not found, attempts to search for JSON file cmap_name in
        specified folder (defaults to app's colormaps folder) for valid colormap.  Returns None
        if no valid colormap could be found."""
        system_colormaps = [m for m in cm.datad]
        if cmap_name in system_colormaps:
            return cm.get_cmap(cmap_name)
        for root, dirs, files in os.walk(usercmaps_folder):
            if cmap_name in files:
                return self.create_cmap(self.get_cmap_dict(os.path.join(root, cmap_name)))
        return None

    def get_cmap_dict(self, json_fname):
        """Returns a colormap dict from the specified JSON file, or None if no colors were found in the dict."""
        colormap = None
        with open(json_fname, "r") as fidin:
            try:
                cmap_dict = json.load(fidin)
                if cmap_dict.get('colors', None) is None:
                    return None
                colormap = cmap_dict
            except ValueError: # Couldn't read file as valid JSON
                return colormap
        return colormap

    def create_cmap(self, cmap_dict):
        """Returns a matplotlib colormap from the cmap_dict.  Returns None if unable to correctly form."""
        if cmap_dict is not None:
            cmap_type = cmap_dict.get('type', 'linear')
            cmap_name = cmap_dict.get('name', None)
            colours = cmap_dict.get('colors', None)
            if cmap_name is None or colors is None:
                return None
            if cmap_type == 'linear':
                return colors.LinearSegmentedColormap.from_list(name=cmap_name, colors=colours)
            else:
                return colors.ListedColormap(name=cmap_name, colors=colours)
        return None

    def save_cmap_dict(self, cmap, output_filename):
        """Saves the colormap dict cmap to output_filename (JSON)."""
        cmap['name'] = os.path.basename(output_filename)
        with open(output_filename, "w") as fidout:
            json.dump(cmap, fidout)

    def generate_sample_data(self):
        """Generates a simple 2D array for previewing colormaps"""
        x,y=np.mgrid[-5:5:0.05,-5:5:0.05]
        return np.sqrt(x**2+y**2)+np.sin(x**2+y**2)