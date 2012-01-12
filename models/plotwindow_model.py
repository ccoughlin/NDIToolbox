"""plotwindow_model.py - Model for plotwindow

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import numpy as np
import scipy.signal

def apply_window(window_type, original_data, start_idx, end_idx):
    """Returns the specified type of window for the range
    start_idx:end_idx, zero outside.  For squelching data outside
    the given range."""
    left = np.zeros(start_idx)
    windows = ['boxcar', 'triang', 'blackman', 'hamming', 'hanning', 'bartlett',
        'parzen', 'bohman', 'blackmanharris', 'nuttall', 'barthann']
    if window_type not in windows:
        middle = np.ones(end_idx-start_idx)
    else:
        middle = scipy.signal.get_window(window_type, end_idx-start_idx)
    right = np.zeros(original_data.shape[0]-end_idx)
    winder = np.concatenate((left, middle, right))
    data = np.multiply(original_data, winder)
    return data