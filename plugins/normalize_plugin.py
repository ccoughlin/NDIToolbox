"""normalize_plugin.py - simple A7117 plugin that normalizes the current
data, used to demonstrate the plugin architecture

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.abstractplugin import TRIPlugin
import numpy as np

class NormalizePlugin(TRIPlugin):
    """Normalizes the current dataset, demonstrates
    how to write plugins for the A7117 project"""

    # At a minimum plugin developers should specify a plugin name and a
    # short description as these are displayed to the user.  The fields
    # required for a plugin are detailed below.
    #
    # Sub-classing a company plugin such as TRIPlugin or
    # ComputationalToolsPlugin will pre-populate these fields with
    # default values.
    name = "Normalize Data" # Name in the Plugin menu
    description = "Normalizes current data set"
    authors = "Chris R. Coughlin (TRI/Austin, Inc.)"
    version = "1.0"
    url = "www.tri-austin.com"
    copyright = "Copyright (C) 2012 TRI/Austin, Inc.  All rights reserved."

    def __init__(self):
        super(NormalizePlugin, self).__init__(self.name, self.description,
            self.authors, self.url, self.copyright)

    def run(self):
        """Executes the plugin - if data are not None they are normalized
        against the largest single element in the array."""
        if self._data is not None:
            max_el = np.max(self._data)
            self._data = self._data / max_el