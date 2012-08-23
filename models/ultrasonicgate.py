"""ultrasonicgate.py - defines a 'gate' (window function) for applying to ultrasonic data

 Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import abstractplugin
import numpy as np

class UltrasonicGate(abstractplugin.AbstractPlugin):
    """Base definition of an ultrasonic gate function"""

    name = "Ultrasonic Gate"
    description = ""
    authors = "TRI/Austin, Inc."
    url = "http://www.nditoolbox.com"
    copyright = ""
    version = "1.0"

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.name)
        self.description = kwargs.get('description', self.description)
        self.authors = kwargs.get('authors', self.authors)
        self.version = kwargs.get('version', self.version)
        self.url = kwargs.get('url', self.url)
        self.copyright = kwargs.get('copyright', self.copyright)
        self.start_idx = kwargs.get('start_pos', 0)
        self.stop_idx = kwargs.get('end_pos', 0)
        self.num_points = self.stop_idx - self.start_idx
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data

    def get_window(self):
        """Returns the window function - data between the start and
        stop indices of the UltrasonicGate will be multiplied by this
        function.  Default window is np.ones (i.e. no-op on data in range)"""
        return np.ones(self.stop_idx - self.start_idx)

    def apply_gate(self):
        """Builds and then executes an ultrasonic gate:  multiplies
        the data by the window function in the range data[self.start_idx:self.stop_idx],
        by zero elsewhere."""
        if self._data is not None:
            # Build the gate function - a standard window function offset from origin.
            # Left of gate - multiply by zero
            left_of_gate = np.zeros(self.start_idx)
            # Middle of gate - multiply by window function
            middle_of_gate = self.get_window()
            # Right of gate - multiply by zero
            right_of_gate = np.zeros(self._data.shape[0] - self.stop_idx)
            completed_gate = np.concatenate((left_of_gate, middle_of_gate, right_of_gate))
            self._data = np.multiply(self._data, completed_gate)

    def run(self):
        """Runs the gate on the data"""
        if self._data is not None:
            self.apply_gate()