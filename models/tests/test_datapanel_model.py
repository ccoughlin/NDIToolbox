"""test_datapanel_model.py - tests the datapanel_model module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import models.datapanel_model
import controllers.pathfinder
import unittest
import os.path

class TestDataPanelModel(unittest.TestCase):
    """Tests the DataPanelModel class"""

    def test_find_data(self):
        """Verify the find_data function"""
        data_dir = controllers.pathfinder.data_path()
        expected_data_files = []
        for root, dirs, paths in os.walk(data_dir):
            for path in paths:
                expected_data_files.append(os.path.join(root, path))
        mock_controller = ""
        model = models.datapanel_model.DataPanelModel(mock_controller)
        self.assertListEqual(expected_data_files, model.find_data())

if __name__ == "__main__":
    unittest.main()