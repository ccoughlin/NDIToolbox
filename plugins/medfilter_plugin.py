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

    def __init__(self, **kwargs):
        TRIPlugin.__init__(self, name=self.name, description=self.description, authors=self.authors,
                           version=self.version, url=self.url, copyright=self.copyright, **kwargs)
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
            # Some types of NDE data (e.g. ultrasonics) frequently package multiple
            # datasets into a single file - TOF, amplitude, and waveform for example.
            # To determine if the plugin has been sent multiple datasets, check for
            # a "keys" attribute to the self._data member, which would indicate a
            # dict has been sent rather than a single array of data
            if hasattr(self._data, "keys"):
                for dataset in self._data:
                    # Execute plugin on every dataset
                    self._data[dataset] = scipy.signal.medfilt(self._data[dataset], kernel_size)
                # You could alternatively execute on one particular type of data
                # e.g.
                # if dataset == "waveform":
                #   self._data = scipy.signal.medfilt(self._data[dataset], kernel_size)
            else:
                # A single dataset was provided
                self._data = scipy.signal.medfilt(self._data, kernel_size)