"""test_pathfinder.py - tests the pathfinder module"""

__author__ = 'Chris R. Coughlin'

import os.path
import unittest
from controllers import pathfinder

class TestPathFinder(unittest.TestCase):
    """Tests the pathfinder module"""

    def setUp(self):
        import __main__
        self.app_path = '/home/ccoughlin/PycharmProjects/Bane'

    def test_app_path(self):
        """Verify pathfinder reports the correct application path"""
        self.assertEqual(self.app_path, pathfinder.app_path())

    def test_resources_path(self):
        """Verify correct resources path"""
        resource_path = os.path.join(self.app_path, 'resources')
        self.assertEqual(resource_path, pathfinder.resource_path())

    def test_icon_path(self):
        """Verify correct icon path"""
        icon_path = os.path.join(self.app_path, 'resources', 'icons')
        self.assertEqual(icon_path, pathfinder.icon_path())

    def test_bitmaps_path(self):
        """Verify correct bitmap path"""
        bmap_path = os.path.join(self.app_path, 'resources', 'bitmaps')
        self.assertEqual(bmap_path, pathfinder.bitmap_path())

    def test_data_path(self):
        """Verify correct data path"""
        data_path = os.path.join(self.app_path, 'data')
        self.assertEqual(data_path, pathfinder.data_path())

    def test_thumbnail_path(self):
        """Verify correct path to data thumbnails"""
        thumb_path = os.path.join(self.app_path, 'thumbnails')
        self.assertEqual(thumb_path, pathfinder.thumbnails_path())

if __name__ == "__main__":
    unittest.main()