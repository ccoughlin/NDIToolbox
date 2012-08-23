"""test_pathfinder.py - tests the pathfinder module"""

__author__ = 'Chris R. Coughlin'

import models
from models.mainmodel import get_config
from controllers import pathfinder
import os.path
import unittest

class TestPathFinder(unittest.TestCase):
    """Tests the pathfinder module"""

    def setUp(self):
        self.app_path = os.path.normcase(os.path.dirname(os.path.dirname(models.__file__)))

    @property
    def user_path(self):
        """Returns the currently-configured user path"""
        cfg = get_config()
        upath_key = "User Path"
        if cfg.has_app_option(upath_key):
            return cfg.get_app_option(upath_key)
        else:
            default_upath = os.path.normcase(os.path.join(os.path.expanduser('~'), 'nditoolbox'))
            cfg.set_app_option({upath_key: default_upath})
            return default_upath

    @property
    def log_path(self):
        """Returns the path to the log file.  If not already set,
        sets to user's home directory/nditoolbox.log and sets the default in the config file."""
        _config = get_config()
        logpath_key = "Log File"
        if _config.has_app_option(logpath_key):
            return _config.get_app_option(logpath_key)
        else:
            default_logpath = os.path.normcase(os.path.join(os.path.expanduser('~'), 'nditoolbox.log'))
            _config.set_app_option({logpath_key: default_logpath})
            return default_logpath

    def test_app_path(self):
        """Verify pathfinder reports the correct application path"""
        self.assertEqual(self.app_path, pathfinder.app_path())

    def test_user_path(self):
        """Verify pathfinder reports the correct path for storing user data"""
        self.assertEqual(self.user_path, pathfinder.user_path())

    def test_resources_path(self):
        """Verify correct resources path"""
        resource_path = os.path.join(self.app_path, 'resources')
        self.assertEqual(resource_path, pathfinder.resource_path())

    def test_icons_path(self):
        """Verify correct icons path"""
        icons_path = os.path.join(self.app_path, 'resources', 'icons')
        self.assertEqual(icons_path, pathfinder.icons_path())

    def test_icon_path(self):
        """Verify correct main application icon path"""
        icon_path = os.path.join(self.app_path, 'resources', 'icons', 'a7117_64.png')
        self.assertEqual(icon_path, pathfinder.icon_path())

    def test_win_icon_path(self):
        """Verify correct main application icon path under Windows"""
        icon_path = os.path.join(self.app_path, 'resources', 'icons', 'a7117_64.ico')
        self.assertEqual(icon_path, pathfinder.winicon_path())

    def test_bitmaps_path(self):
        """Verify correct bitmap path"""
        bmap_path = os.path.join(self.app_path, 'resources', 'bitmaps')
        self.assertEqual(bmap_path, pathfinder.bitmap_path())

    def test_textfiles_path(self):
        """Verify correct text files path"""
        help_path = os.path.join(self.app_path, 'resources', 'textfiles')
        self.assertEqual(help_path, pathfinder.textfiles_path())

    def test_data_path(self):
        """Verify correct data path"""
        data_path = os.path.join(self.user_path, 'data')
        self.assertEqual(data_path, pathfinder.data_path())

    def test_thumbnail_path(self):
        """Verify correct path to data thumbnails"""
        thumb_path = os.path.join(self.user_path, 'thumbnails')
        self.assertEqual(thumb_path, pathfinder.thumbnails_path())

    def test_plugins_path(self):
        """Verify correct path to plugins"""
        plugin_path = os.path.join(self.user_path, 'plugins')
        self.assertEqual(plugin_path, pathfinder.plugins_path())

    def test_podmodels_path(self):
        """Verify correct path to POD Toolkit models"""
        model_path = os.path.join(self.user_path, "podmodels")
        self.assertEqual(model_path, pathfinder.podmodels_path())

    def test_gates_path(self):
        """Verify correct path to ultrasonic gates"""
        gates_path = os.path.join(self.user_path, "gates")
        self.assertEqual(gates_path, pathfinder.gates_path())

    def test_config_path(self):
        """Verify correct path to configuration file"""
        config_path = os.path.normcase(os.path.expanduser("~/nditoolbox.cfg"))
        self.assertEqual(config_path, pathfinder.config_path())

    def test_docs_path(self):
        """Verify correct path to documents folder"""
        doc_path = os.path.join(self.app_path, 'docs')
        self.assertEqual(doc_path, pathfinder.docs_path())

    def test_log_path(self):
        """Verify returning correct path to log file"""
        self.assertEqual(self.log_path, pathfinder.log_path())

if __name__ == "__main__":
    unittest.main()