"""podtk_model.py - model for the POD Toolkit

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
from models import abstractplugin
from models import mainmodel
from models import dataio
from configobj import ConfigObj
import numpy as np
import os.path

class PODWindowModel(object):
    """Model for the PODWindow UI"""

    def __init__(self, controller):
        self.controller = controller

    def load_models(self):
        """Searches the POD Models folder and imports all valid models,
        returning a list of the models successfully imported as tuples:
        first element is the model name (e.g. AHat_v_A), second element is
        the class of the model."""
        return mainmodel.load_dynamic_modules(pathfinder.podmodels_path(), PODModel)

    @classmethod
    def load_data(cls, file_name):
        """Returns NumPy array from the specified file."""
        return dataio.get_data(file_name)

    @classmethod
    def load_csv(cls, file_name):
        """Returns NumPy array from the specified CSV file."""
        return np.genfromtxt(file_name, delimiter=",")

    @classmethod
    def save_data(cls, file_name, data):
        """Saves NumPy array data to the specified file name"""
        dataio.save_data(file_name, data)

    @classmethod
    def save_csv(cls, file_name, data):
        """Saves NumPy array data as CSV data"""
        np.savetxt(file_name, data, delimiter=",")


class PODModel(abstractplugin.AbstractPlugin):
    """Base analysis class for the POD Toolkit"""
    description = ""
    inputdata = {}
    params = {}
    settings = {}

    def __init__(self, name, description=None, inputdata=None, params=None,
                 settings=None):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if inputdata is not None:
            self.inputdata = inputdata
        if params is not None:
            self.params = params
        if settings is not None:
            self.settings = settings
        self._data = None
        self.config = os.path.join(pathfinder.podmodels_path(), self.__module__ + '.cfg')
        self.results = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data

    def run(self):
        """Executes the plugin (no-op in base class)"""
        pass

    def plot1(self, axes_hdl):
        """Generates the primary plot on the specified matplotlib Axes instance
        (no-op in base class)."""
        pass

    def plot2(self, axes_hdl):
        """Generates the secondary plot on the specified matplotlib Axes instance
        (no-op in base class)."""
        pass

    def configure(self):
        """Reads the PODModel's configuration file and configures
        the model accordingly."""
        if self.config is not None:
            if os.path.exists(self.config):
                config = ConfigObj(self.config)
                config_keys = config.keys()
                if 'Input Data' in config_keys:
                    self.inputdata = config['Input Data']
                if 'Parameters' in config_keys:
                    self.params = config['Parameters']
                if 'Settings' in config_keys:
                    self.settings = config['Settings']

    def save_configuration(self):
        """Saves the current configuration to disk"""
        if self.config is not None:
            config = ConfigObj(self.config)
            config['Input Data'] = self.inputdata
            config['Parameters'] = self.params
            config['Settings'] = self.settings
            config.write()