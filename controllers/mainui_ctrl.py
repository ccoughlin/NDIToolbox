''' mainui_ctrl.p - controller for mainui

Chris R. Coughlin (TRI/Austin, Inc.)
'''

__author__ = 'Chris R. Coughlin'

from models import mainmodel

class MainUIController(object):
    '''Controller for the main user interface'''

    def __init__(self, view):
        self.view = view
        self.init_model()

    def init_model(self):
        '''Creates and connects the model'''
        self.model = mainmodel.MainModel()

    def set_thumb(self, panel, data_file, enable=True):
        '''Sets the bitmap contents of the specified panel to a thumbnail
        plot of the selected data file, or a placeholder bitmap if thumbnails
        are disabled.'''
        if enable:
            panel.plot_thumb(data_file)
        else:
            panel.plot_blank()