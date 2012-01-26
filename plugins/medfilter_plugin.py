"""medfilter_plugin.py - applies a median filter to the current data set,
used to demonstrate incorporating UI elements in an A7117 plugin

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.triplugin import TRIPlugin
import scipy.signal

class MedianFilterPlugin(TRIPlugin):
    """Applies a median filter to the
    current data set"""

    name = "Median Filter"
    description = "Applies a median filter to the current data set."

    def __init__(self):
        super(MedianFilterPlugin, self).__init__(self.name, self.description,
                                                 self.authors, self.url, self.copyright)
        self.config = {'kernel size':3}

    def run(self):
        """Runs the plugin, asking the user to specify a kernel size for the median filter.
        A filter of rank A where A is the specified kernel size is then applied to the
        current data set in each dimension."""
        if self._data is not None:
            kernel_size = int(self.config.get('kernel size', 3))
            self._data = scipy.signal.medfilt(self._data,
                                              kernel_size)