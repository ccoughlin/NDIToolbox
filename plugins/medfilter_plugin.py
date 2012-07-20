"""medfilter_plugin.py - applies a median filter to the current data set,
used to demonstrate incorporating configuration options in a NDIToolbox plugin

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.abstractplugin import TRIPlugin
import scipy.signal

class MedianFilterPlugin(TRIPlugin):
    """Applies a median filter to the
    current data set"""

    name = "Median Filter"
    description = "Applies a median filter to the current data set."

    def __init__(self):
        super(MedianFilterPlugin, self).__init__(self.name, self.description,
                                                 self.authors, self.url, self.copyright)
        # If a config dict is defined in a Plugin, the UI will present the user
        # with a dialog box allowing run-time configuration (populated with the
        # default values set here).  Although vals can be of any pickle-able type,
        # they are returned as str.
        self.config = {'kernel size': '3'}

    def run(self):
        """Runs the plugin, asking the user to specify a kernel size for the median filter.
        A filter of rank A where A is the specified kernel size is then applied to the
        current data set in each dimension.  An even kernel size is automatically
        incremented by one to use an odd number-SciPy's medfilt function requires odd
        numbers for kernel size.
        """
        if self._data is not None:
            # The UI returns configuration options as str - the Plugin is
            # responsible for casting them to required type
            kernel_size = int(self.config.get('kernel size', 3))
            if kernel_size % 2 == 0:
                # medfilt function requires odd number for kernel size
                kernel_size += 1
            self._data = scipy.signal.medfilt(self._data,
                                              kernel_size)