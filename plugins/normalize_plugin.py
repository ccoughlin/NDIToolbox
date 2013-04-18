"""normalize_plugin.py - simple NDIToolbox plugin that normalizes the current
data, used to demonstrate the plugin architecture

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.abstractplugin import TRIPlugin
import numpy as np

class NormalizePlugin(TRIPlugin):
    """Normalizes the current dataset, demonstrates
    how to write plugins for the NDIToolbox application"""

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
    version = "1.1"
    url = "www.tri-austin.com"
    copyright = "Copyright (C) 2013 TRI/Austin, Inc.  All rights reserved."

    def __init__(self, **kwargs):
        TRIPlugin.__init__(self, name=self.name, description=self.description, authors=self.authors,
                           version=self.version, url=self.url, copyright=self.copyright, **kwargs)

    def run(self):
        """Executes the plugin - if data are not None they are normalized
        against the largest single element in the array."""
        if self._data is not None:
            # Some types of NDE data (e.g. ultrasonics) frequently package multiple
            # datasets into a single file - TOF, amplitude, and waveform for example.
            # To determine if the plugin has been sent multiple datasets, check for
            # a "keys" attribute to the self._data member, which would indicate a
            # dict has been sent rather than a single array of data
            if hasattr(self._data, "keys"):
                for dataset in self._data:
                    # Execute plugin on every dataset
                    max_el = np.max(self._data[dataset])
                    self._data[dataset] /= max_el
                # You could alternatively execute on one particular type of data
                # e.g.
                # if dataset == "amplitude":
                #   max_el = np.max(self._data[dataset])
                #   self._data[dataset] /= max_el
            else:
                # A single dataset was provided
                max_el = np.max(self._data)
                self._data /= max_el