"""test_uimodel.py - tests the uimodel module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'ccoughlin'

import unittest
from models import colormapcreator_model
import numpy as np
from matplotlib import colors
from matplotlib import cm
import os
import os.path
import json

class TestColormapCreatorModel(unittest.TestCase):
    """Tests the ColormapCreatorModel class"""
    good_cmap_file = os.path.join(os.path.dirname(__file__), "support_files", "good_cmap")
    bad_cmap_file = os.path.join(os.path.dirname(__file__), "support_files", "bad_cmap")

    def setUp(self):
        self.model = colormapcreator_model.ColormapCreatorModel(controller="")

    def test_get_cmap(self):
        """Verify get_cmap returns a valid matplotlib colormap"""
        system_colormaps = [m for m in cm.datad]
        for cmap_name in system_colormaps:
            self.assertTrue(isinstance(self.model.get_cmap(cmap_name), colors.Colormap))
        self.assertTrue(isinstance(self.model.get_cmap("good_cmap", usercmaps_folder=os.path.dirname(__file__)),
                                   colors.Colormap))
        self.assertIsNone(self.model.get_cmap("bad_cmap", usercmaps_folder=os.path.dirname(__file__)))

    def test_get_cmap_dict(self):
        """Verify get_cmap_dict returns a colormap dict from the JSON"""
        # Good file
        with open(TestColormapCreatorModel.good_cmap_file, "r") as fidin:
            good_cmap_dict = json.load(fidin)
            self.assertDictEqual(good_cmap_dict, self.model.get_cmap_dict(TestColormapCreatorModel.good_cmap_file))
            # Bad file
        with open(TestColormapCreatorModel.bad_cmap_file, "r") as fidin:
            self.assertIsNone(self.model.get_cmap_dict(TestColormapCreatorModel.bad_cmap_file))
            # Not a colormap file
        with open(__file__, "r") as fidin:
            self.assertIsNone(self.model.get_cmap_dict(__file__))

    def test_create_cmap(self):
        """Verify create_cmap returns a valid matplotlib colormap"""
        self.assertTrue(isinstance(self.model.create_cmap(self.model.get_cmap_dict(TestColormapCreatorModel.good_cmap_file)),
                                   colors.Colormap))
        self.assertIsNone(self.model.create_cmap(self.model.get_cmap_dict(TestColormapCreatorModel.bad_cmap_file)))
        self.assertIsNone(self.model.create_cmap(self.model.get_cmap_dict(__file__)))

    def test_save_cmap_dict(self):
        """Verify storing the colormap dict"""
        sample_cmap_dict = {'colors':[[0,0],[1,1],[2,2]],
                            'type':'list'}
        output_path = os.path.join(os.path.join(os.path.dirname(__file__), "test_save_cmap_dict_output"))
        self.model.save_cmap_dict(sample_cmap_dict, output_path)
        self.assertTrue(os.path.exists(output_path))
        self.assertDictEqual(sample_cmap_dict, self.model.get_cmap_dict(output_path))
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except WindowsError: # File in use
                pass

    def test_generate_sample_data(self):
        """Verify generate_sample_data returns a 2D NumPy array"""
        returned_array = self.model.generate_sample_data()
        self.assertTrue(isinstance(returned_array, np.ndarray))
        self.assertEqual(returned_array.ndim, 2)

if __name__ == "__main__":
    unittest.main()