"""podtk_model.py - model for the POD Toolkit

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
from models import abstractplugin
from models import mainmodel
from configobj import ConfigObj
import imp
import inspect
import os.path
import sys

class PODWindowModel(object):
    """Model for the PODWindow UI"""

    def __init__(self, controller):
        self.controller = controller

    def load_models(self):
        """Searches the POD Models folder and imports all valid models,
        returning a list of the models successfully imported as tuples:
        first element is the model name (e.g. AHat_v_A), second element is
        the class of the model."""
        models_folder = pathfinder.podmodels_path()
        pod_models = []
        if not models_folder in sys.path:
            sys.path.append(models_folder)
        for root, dir, files in os.walk(pathfinder.podmodels_path()):
            for model_file in files:
                model_name, model_extension = os.path.splitext(model_file)
                module_hdl = None
                if model_extension == os.extsep + "py":
                    try:
                        module_hdl, path_name, description = imp.find_module(model_name)
                        podmodel_module = imp.load_module(model_name, module_hdl, path_name,
                            description)
                        podmodel_classes = inspect.getmembers(podmodel_module, inspect.isclass)
                        for podmodel_class in podmodel_classes:
                            if issubclass(podmodel_class[1], PODModel):
                                if podmodel_class[1].__module__ == model_name:
                                    pod_models.append(podmodel_class)
                    finally:
                        if module_hdl is not None:
                            module_hdl.close()
        return pod_models

    @classmethod
    def load_data(cls, file_name):
        """Returns NumPy array from the specified CSV file."""
        import_params = {'delimiter': ','}
        return mainmodel.get_data(file_name, **import_params)

    @classmethod
    def save_data(cls, file_name, data):
        """Saves NumPy array data to the specified file name"""
        export_params = {'delimiter': ','}
        mainmodel.save_data(file_name, data, **export_params)


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