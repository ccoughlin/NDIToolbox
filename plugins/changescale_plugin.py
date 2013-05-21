"""changescale_plugin.py - convenience utility to perform linear conversion between signal scales, e.g.
converting from data stored as integers back into voltages, converting between Fahrenheit and Celsius, etc.

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'ccoughlin'

from models.abstractplugin import TRIPlugin
import math


class ChangeScalePlugin(TRIPlugin):
    """Linear conversion between signal scales"""

    name = "Change Scale"
    description = "Linear conversion between signal measurement scales (e.g. volts to microvolts)"

    def __init__(self, **kwargs):
        TRIPlugin.__init__(self, name=self.name, description=self.description, authors=self.authors,
                           version=self.version, url=self.url, copyright=self.copyright, **kwargs)
        self.config = {'Original Scale Minimum': '0',
                       'Original Scale Maximum': '1',
                       'New Scale Minimum': '0',
                       'New Scale Maximum': '1'}

    def calculate_scale_conversion_factors(self):
        """Calculates the slope and offset required to convert the data from its
        original scale to the new scale"""
        orig_scale_min = float(self.config.get('Original Scale Minimum', 0))
        orig_scale_max = float(self.config.get('Original Scale Maximum', 1))
        new_scale_min = float(self.config.get('New Scale Minimum', 0))
        new_scale_max = float(self.config.get('New Scale Maximum', 1))
        self.scale_conversion_factor = (new_scale_max - new_scale_min) / (orig_scale_max - orig_scale_min)
        self.scale_offset = new_scale_max - self.scale_conversion_factor * orig_scale_max

    def run(self):
        """Runs the plugin, asking the user to specify a kernel size for the median filter.
        A filter of rank A where A is the specified kernel size is then applied to the
        current data set in each dimension.  An even kernel size is automatically
        incremented by one to use an odd number-SciPy's medfilt function requires odd
        numbers for kernel size.
        """
        self.calculate_scale_conversion_factors()
        if self._data is not None:
            # The UI returns configuration options as str - the Plugin is
            # responsible for casting them to required type
            if hasattr(self._data, "keys"):
                for dataset in self._data:
                    # Execute plugin on every dataset
                    self._data[dataset] = self._data[dataset] * self.scale_conversion_factor + self.scale_offset
            else:
                # A single dataset was provided
                self._data = self._data * self.scale_conversion_factor + self.scale_offset