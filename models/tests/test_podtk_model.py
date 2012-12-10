"""test_podtk_model.py - tests the podtk_model module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import unittest
from models import podtk_model
from models import configobj
from controllers import pathfinder
import h5py
import numpy as np
import os
import random
import shutil

class TestPODWindowModel(unittest.TestCase):
    """Tests the PODWindowModel class"""

    def setUp(self):
        self.mock_controller = ""
        self.model = podtk_model.PODWindowModel(controller=self.mock_controller)
        self.sample_data = np.array(self.random_data())
        self.sample_data_basename = "sample.dat"
        self.sample_data_file = os.path.join(os.path.dirname(__file__),
                                             self.sample_data_basename)
        self.sample_csvdata_basename = "sample.csv"
        self.sample_csvdata_file = os.path.join(os.path.dirname(__file__), self.sample_csvdata_basename)
        np.savetxt(self.sample_csvdata_file, self.sample_data, delimiter=",")
        with h5py.File(self.sample_data_file, 'w') as fidout:
            fidout.create_dataset(self.sample_data_basename, data=self.sample_data)

    def random_data(self):
        """Returns a list of random data"""
        return [random.uniform(-100, 100) for i in range(25)]

    def test_load_models(self):
        """Tests the load_models method"""
        pod_models = self.model.load_models()
        for model_name, model_class in pod_models:
            # Basic check to ensure the returned POD Model name is in the class name
            self.assertTrue(model_name in str(model_class))
            # Ensure the returned class is a PODModel
            self.assertTrue(issubclass(model_class, podtk_model.PODModel))

    def test_load_data(self):
        """Verify load_data classmethod returns correct data"""
        read_data = self.model.load_data(self.sample_data_file)
        self.assertTrue(np.array_equal(self.sample_data, read_data))

    def test_load_csv(self):
        """Verify load_csv classmethod returns correct data"""
        read_data = self.model.load_csv(self.sample_csvdata_file)
        self.assertTrue(np.array_equal(self.sample_data, read_data))

    def test_save_data(self):
        """Verify save_data classmethod correctly saves data"""
        if os.path.exists(self.sample_data_file + ".hdf5"):
            os.remove(self.sample_data_file + ".hdf5")
        self.model.save_data(self.sample_data_file, self.sample_data)
        assert(os.path.exists(self.sample_data_file + ".hdf5"))
        returned_data = self.model.load_data(self.sample_data_file + ".hdf5")
        self.assertTrue(np.array_equal(returned_data, self.sample_data))

    def test_save_csv(self):
        if os.path.exists(self.sample_csvdata_file):
            os.remove(self.sample_csvdata_file)
        self.model.save_csv(self.sample_csvdata_file, self.sample_data)
        assert(os.path.exists(self.sample_csvdata_file))
        returned_data = self.model.load_csv(self.sample_csvdata_file)
        self.assertTrue(np.array_equal(returned_data, self.sample_data))

    def tearDown(self):
        for sample_file in [self.sample_csvdata_file, self.sample_data_file, self.sample_data_file+".hdf5"]:
            if os.path.exists(sample_file):
                try:
                    os.remove(sample_file)
                except WindowsError: # file in use (Windows)
                    pass


class TestPODModel(unittest.TestCase):
    """Tests the PODModel class"""

    def setUp(self):
        self.config_file = os.path.join(pathfinder.podmodels_path(), 'sample_podmodel.cfg')
        if not os.path.exists(self.config_file):
            shutil.copy(self.path_to_support_file('sample_podmodel.cfg'), self.config_file)
        self.pod_file = os.path.join(pathfinder.podmodels_path(), 'sample_podmodel.py')
        if not os.path.exists(self.pod_file):
            shutil.copy(self.path_to_support_file('sample_podmodel.py'), self.pod_file)

    def path_to_support_file(self, base_fname):
        """Returns the full path to the support file"""
        cur_dir = os.getcwd()
        if os.path.normcase(cur_dir) == os.path.normcase(os.path.dirname(__file__)):
            # Running this test module directly
            return os.path.join('support_files', base_fname)
        else:
            # Running as part of larger project test suite
            return os.path.join('models', 'tests', 'support_files', base_fname)

    def test_init(self):
        """Verify basic settings for initialization"""
        pod_model = MockPODModel(self.config_file)
        self.assertIsNotNone(pod_model.config)
        self.assertIsNone(pod_model._data)
        self.assertIsNone(pod_model.results)

    def test_configure(self):
        """Verify the POD Model can configure itself"""
        config = configobj.ConfigObj(self.config_file)
        pod_model = MockPODModel(self.config_file)
        pod_model.configure()
        self.assertDictEqual(config['Input Data'], pod_model.inputdata)
        self.assertDictEqual(config['Parameters'], pod_model.params)
        self.assertDictEqual(config['Settings'], pod_model.settings)

    def test_save_configuration(self):
        """Verify the POD Model can save its configuration"""
        pod_model = MockPODModel(self.config_file)
        pod_model.configure()
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        pod_model.save_configuration()
        config = configobj.ConfigObj(self.config_file)
        self.assertDictEqual(config['Input Data'], pod_model.inputdata)
        self.assertDictEqual(config['Parameters'], pod_model.params)
        self.assertDictEqual(config['Settings'], pod_model.settings)

    def tearDown(self):
        try:
            if os.path.exists(self.pod_file):
                os.remove(self.pod_file)
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
        except WindowsError: # file in use in Windows
            return


class MockPODModel(podtk_model.PODModel):
    """Generic PODModel subclass for verifying basic
    PODModel operations"""

    name = "Sample POD Model"
    description = "Generic POD Model used in unit tests"
    authors = "TRI/Austin, Inc."
    version = "1.0"
    url = "www.nditoolbox.com"
    copyright = "Copyright (C) 2012 TRI/Austin, Inc."


    def __init__(self, config_file):
        """Mocks PODModel by allowing a specified configuration file"""
        podtk_model.PODModel.__init__(self, self.name, self.description,
                                      self.inputdata, self.params, self.settings)
        self.config = config_file

    def run(self):
        pass

    def plot1(self, axes_hdl):
        pass

    def plot2(self, axes_hdl):
        pass

if __name__ == "__main__":
    unittest.main()