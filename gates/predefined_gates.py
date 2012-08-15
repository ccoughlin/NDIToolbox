"""predefined_gates.py - defines ultrasonic 'gate' functions (offset windows)
from SciPy's built-in scipy.signal windows

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.ultrasonicgate import UltrasonicGate
import scipy.signal

class Boxcar(UltrasonicGate):
    """Wrapper for the boxcar window function"""

    name = "Boxcar Gate"
    description = "Provides the boxcar gate function"

    def get_window(self):
        """Returns the window function for the gate - data
        are multiplied with this function"""
        return scipy.signal.get_window("boxcar", self.num_points)

class Triangular(UltrasonicGate):
    """Wrapper for the triang window function"""

    name = "Triangular Gate"
    description = "Provides the triangular gate function"

    def get_window(self):
        return scipy.signal.get_window("triang", self.num_points)

class Blackman(UltrasonicGate):
    """Wrapper for the blackman window function"""

    name = "Blackman Gate"
    description = "Provides the Blackman gate function"

    def get_window(self):
        return scipy.signal.get_window("blackman", self.num_points)

class Hamming(UltrasonicGate):
    """Wrapper for the hamming window function"""

    name = "Hamming Gate"
    description = "Provides the Hamming gate function"

    def get_window(self):
        return scipy.signal.get_window("hamming", self.num_points)

class Hanning(UltrasonicGate):
    """Wrapper for the hanning window function"""

    name = "Hanning Gate"
    description = "Provides the Hann (also known as Hanning) gate function"

    def get_window(self):
        return scipy.signal.get_window("hann", self.num_points)

class Bartlett(UltrasonicGate):
    """Wrapper for the bartlett window function"""

    name = "Bartlett Gate"
    description = "Provides the Bartlett gate function"

    def get_window(self):
        return scipy.signal.get_window("bartlett", self.num_points)

class Parzen(UltrasonicGate):
    """Wrapper for the parzen window function"""

    name = "Parzen Gate"
    description = "Provides the Parzen gate function"

    def get_window(self):
        return scipy.signal.get_window("parzen", self.num_points)

class Bohman(UltrasonicGate):
    """Wrapper for the bohman window function"""

    name = "Bohman Gate"
    description = "Provides the Bohman gate function"

    def get_window(self):
        return scipy.signal.get_window("bohman", self.num_points)

class BlackmanHarris(UltrasonicGate):
    """Wrapper for the blackmanharris window function"""

    name = "Blackman-Harris Gate"
    description = "Provides the Blackman-Harris gate function (a generalization of the Hamming gate)"

    def get_window(self):
        return scipy.signal.get_window("blackmanharris", self.num_points)

class Nuttall(UltrasonicGate):
    """Wrapper for the nuttall window function"""

    name = "Nuttall Gate"
    description = "Provides the Nuttall gate function"

    def get_window(self):
        return scipy.signal.get_window("nuttall", self.num_points)

class BartlettHann(UltrasonicGate):
    """Wrapper for the barthann window function"""

    name = "Bartlett-Hann Gate"
    description = "Provides the Bartlett-Hann gate function"

    def get_window(self):
        return scipy.signal.get_window("barthann", self.num_points)

class Kaiser(UltrasonicGate):
    """Wrapper for the kaiser window function"""

    name = "Kaiser Gate"
    description = "Provides the Kaiser gate function (simple approximation of the DPSS)"
    default_beta = 0.5

    def __init__(self, **kwargs):
        UltrasonicGate.__init__(self, **kwargs)
        self.config = {'beta':Kaiser.default_beta}

    @property
    def beta(self):
        """Returns the current value of the beta parameter, or Kaiser.default_beta
        if unavailable."""
        try:
            return float(self.config.get('beta', Kaiser.default_beta))
        except ValueError: # couldn't convert beta value to float
            return Kaiser.default_beta

    def get_window(self):
        return scipy.signal.get_window(('kaiser', self.beta), self.num_points)

class Gaussian(UltrasonicGate):
    """Wrapper for the gaussian window function"""

    name = "Gaussian Gate"
    description = "Provides the Gaussian gate function"
    default_std = 2.5

    def __init__(self, **kwargs):
        UltrasonicGate.__init__(self, **kwargs)
        self.config = {'std':Gaussian.default_std}

    @property
    def std(self):
        """Returns the current value of the std parameter, or
        Gaussian.default_std if unavailable."""
        try:
            return float(self.config.get('std', Gaussian.default_std))
        except ValueError: # couldn't convert std to float
            return Gaussian.default_std

    def get_window(self):
        return scipy.signal.get_window(('gaussian', self.std), self.num_points)

class GeneralGaussian(UltrasonicGate):
    """Wrapper for the general_gaussian window function"""

    name = "General Gaussian Gate"
    description = "Provides the general Gaussian gate function"
    default_power = 1.0
    default_width = 1.0

    def __init__(self, **kwargs):
        UltrasonicGate.__init__(self, **kwargs)
        self.config = {'power':GeneralGaussian.default_power,
                       'width':GeneralGaussian.default_width}

    @property
    def power(self):
        """Returns the value of the power parameter, or GeneralGaussian.default_power
        if not available."""
        try:
            return float(self.config.get('power', GeneralGaussian.default_power))
        except ValueError: # couldn't convert power to float
            return GeneralGaussian.default_power

    @property
    def width(self):
        """Returns the value of the width parameter, or GeneralGaussian.default_width
        if not available."""
        try:
            return float(self.config.get('width', GeneralGaussian.default_width))
        except ValueError: # couldn't convert width to float
            return GeneralGaussian.default_width

class Slepian(UltrasonicGate):
    """Wrapper for the slepian window function"""

    name = "DPSS (Slepian) Gate"
    description = "Provides the  DPSS (Digital Prolate Spheroidal Sequence,\nalso known as the Slepian) gate function"
    width_product_limit = 27.38 # In SciPy's Slepian implementation width*num_points < 27.38

    def __init__(self, **kwargs):
        UltrasonicGate.__init__(self, **kwargs)
        self.config = {'width':'auto'}

    @property
    def width(self):
        """Returns the value of the width parameter, or an automatically-determined
        value if not available.  The auto value is determined by the SciPy requirement
        that the number of points * the width must be less than 27.38, i.e,

        self.width * self.num_points < 27.38

        The auto value is chosen to meet this constraint but otherwise has no real
        significance.  Users are encouraged to read more about the DPSS window
        (e.g. https://ccrma.stanford.edu/~jos/sasp/Slepian_DPSS_Window.html ) to
        determine proper settings for their application.
        """
        # Define a default 'safe' value for scipy.signal.slepian
        width_value = (Slepian.width_product_limit / self.num_points)*.95
        width_setting = self.config.get('width', 'auto')
        if width_setting.lower() != 'auto':
            try:
                width_value = float(self.config.get('width', width_value))
            except ValueError: # couldn't convert width to float
                pass
        return width_value

    def get_window(self):
        return scipy.signal.get_window(('slepian', self.width), self.num_points)