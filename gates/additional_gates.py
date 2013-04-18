"""additional_gates.py - provides ultrasonic gate functions in addition to the built-in scipy.signal gates

Chris R. Coughlin (TRI/Austin, Inc).
"""

__author__ = 'Chris R. Coughlin'

from models.ultrasonicgate import UltrasonicGate
import numpy as np
import math

class Sine(UltrasonicGate):
    """Provides a standard sine (also known as a cosine) gate function"""

    name = "Sine Gate"
    description = "Provides the sine (also known as a cosine) gate function"

    def get_window(self):
        window_array = []
        for el in range(self.num_points):
            fpoint = float(el)
            window_array.append(math.sin((math.pi * fpoint) / (self.num_points - 1)))
        return np.array(window_array)


class Lanczos(UltrasonicGate):
    """Provides a Lanczos (normalized sinc) gate function"""

    name = "Lanczos Gate"
    description = "Provides the Lanczos (normalized sinc) gate function"

    def get_window(self):
        window_array = []
        for el in range(self.num_points):
            point = 2 * float(el) / (self.num_points - 1) - 1
            window_array.append(self.normalized_sinc(point))
        return np.array(window_array)

    def normalized_sinc(self, x):
        """Returns the normalized sinc of the point x."""
        try:
            return math.sin(math.pi * x) / (math.pi * x)
        except ZeroDivisionError:
            return 1


class Tukey(UltrasonicGate):
    """Provides a Tukey gate function"""

    name = "Tukey Gate"
    description = "Provides the Tukey (also known as the tapered cosine) gate function"
    default_alpha = 0.5

    def __init__(self, **kwargs):
        UltrasonicGate.__init__(self, **kwargs)
        self.config = {'alpha': Tukey.default_alpha}

    @property
    def alpha(self):
        """Returns the current setting for alpha, or the default alpha value for the
        gate if unavailable."""
        try:
            return float(self.config.get('alpha', Tukey.default_alpha))
        except ValueError: # alpha setting couldn't be converted to a float
            return Tukey.default_alpha

    def left_lobe(self):
        """Returns the left cosine lobe of the window"""
        left_lobe_array = []
        lower_limit = 0
        upper_limit = self.alpha * (self.num_points - 1) / 2
        for point in range(lower_limit, int(upper_limit)):
            fpoint = float(point)
            left_lobe_array.append(
                .5 * (1 + math.cos(math.pi * (2 * fpoint / (self.alpha * (self.num_points - 1)) - 1))))
        return np.array(left_lobe_array)

    def middle(self):
        """Returns the middle rectangular portion of the window"""
        lower_limit = self.alpha * (self.num_points - 1) / 2
        upper_limit = (self.num_points - 1) * (1 - 0.5 * self.alpha)
        return np.ones(int(upper_limit) - int(lower_limit))

    def right_lobe(self):
        """Returns the right cosine lobe of the window"""
        right_lobe_array = []
        lower_limit = (self.num_points - 1) * (1 - 0.5 * self.alpha)
        upper_limit = self.num_points - 1
        for point in range(int(lower_limit), int(upper_limit)):
            fpoint = float(point)
            right_lobe_array.append(
                .5 * (1 + math.cos(math.pi * (2 * fpoint / (self.alpha * (self.num_points - 1)) - 2 / self.alpha + 1))))
        return np.array(right_lobe_array)
