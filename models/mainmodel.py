""" mainmodel.py - primary model for the project

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import numpy as np

def get_data(data_fname, **import_params):
    """Loads the data from an ASCII-delimited text file"""
    comment_char = import_params.get('commentchar', '#')
    delim_char = import_params.get('delimiter', None)
    header_lines = import_params.get('skipheader', 0)
    footer_lines = import_params.get('skipfooter', 0)
    cols_to_read = import_params.get('usecols', None)
    transpose_data = import_params.get('transpose', False)
    data = np.genfromtxt(data_fname, comments=comment_char, delimiter=delim_char,
        skip_header=header_lines, skip_footer=footer_lines, usecols=cols_to_read,
        unpack=transpose_data)
    return data

class MainModel(object):
    pass