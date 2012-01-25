"""medfilter_plugin.py - applies a median filter to the current data set,
used to demonstrate incorporating UI elements in an A7117 plugin

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.triplugin import TRIPlugin
import scipy.signal
import wx

class MedianFilterPlugin(TRIPlugin):
    """Applies a median filter to the
    current data set"""

    name = "Median Filter"
    description = "Applies a median filter to the current data set"

    def __init__(self):
        super(MedianFilterPlugin, self).__init__(self.name, self.description,
                                                 self.authors, self.url, self.copyright)

    def run(self):
        """Runs the plugin, asking the user to specify a kernel size for the median filter.
        A filter of rank A where A is the specified kernel size is then applied to the
        current data set in each dimension."""
        if self._data is not None:
            # Since the main UI is wxPython, we don't need to use the standard wxPython
            # UI initialization code.  A plugin using PyQt, Tkinter, etc. would be
            # responsible for creating and initializing the GUI.
            kernelsize_dlg = wx.NumberEntryDialog(parent=None,
                                                  message="Please specify the kernel size to use.",
                                                  prompt="Kernel Size:",
                                                  caption="Set Kernel Size",
                                                  value=3, min=1, max=self._data.size,
                                                  pos=wx.DefaultPosition)
            if kernelsize_dlg.ShowModal() == wx.ID_OK:
                self._data = scipy.signal.medfilt(self._data,
                                                  kernel_size=kernelsize_dlg.GetValue())
            # We're responsible for closing the dialog
            kernelsize_dlg.Destroy()