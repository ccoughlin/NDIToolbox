"""test_config.py - tests the config module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import unittest
from models import config
from controllers import pathfinder
import ConfigParser
import os
import os.path

class TestConfigure(unittest.TestCase):

    def setUp(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "tst_config.cfg")
        self.config = config.Configure(self.config_path)

    def write_cfg(self):
        """Write some basic configuration options to the config file"""
        self.config.set_app_option({'path':pathfinder.app_path()})
        self.config.set_app_option({'Should Run':False})
        self.config.set_app_option({'alpha':1, 'beta':-2.2})
        self.config.set_app_option({'labels':('mon', 'wed', 'fri', 3.14)})
        self.config.set(section='Plugins', options={'medfilter':True,
                                                    'normalize':False})
        self.config.set(section='Coordinates', options={'app':(21,-42)})
        self.config.set(section='Coordinates', options={'alpha':1, 'beta':-2.2})

    def configparser_reader(self):
        """Returns a SafeConfigParser instance with the config file
        read"""
        config_reader = ConfigParser.SafeConfigParser()
        config_reader.read(self.config_path)
        return config_reader

    def test_write_sections(self):
        """Verify creation of new sections"""
        self.write_cfg()
        config_reader = self.configparser_reader()
        self.assertTrue(config_reader.has_section('Application'))
        self.assertTrue(config_reader.has_section('Plugins'))
        self.assertTrue(config_reader.has_section('Coordinates'))

    def test_write_options(self):
        """Verify creation of new string options"""
        self.write_cfg()
        config_reader = self.configparser_reader()
        self.assertTrue(config_reader.has_option('Application', 'path'))
        self.assertTrue(config_reader.has_option('Application', 'Should Run'))
        self.assertTrue(config_reader.has_option('Application', 'alpha'))
        self.assertTrue(config_reader.has_option('Application', 'beta'))
        self.assertTrue(config_reader.has_option('Application', 'labels'))
        self.assertTrue(config_reader.has_option('Plugins', 'medfilter'))
        self.assertTrue(config_reader.has_option('Plugins', 'normalize'))
        self.assertTrue(config_reader.has_option('Coordinates', 'app'))
        self.assertTrue(config_reader.has_option('Coordinates', 'alpha'))
        self.assertTrue(config_reader.has_option('Coordinates', 'beta'))

    def test_read_options(self):
        """Verify reading of options"""
        self.write_cfg()
        self.assertEqual(pathfinder.app_path(),
            self.config.get_app_option('path'))
        self.assertFalse(self.config.get_app_option_boolean('Should Run'))
        self.assertEqual(self.config.get_app_option_int('alpha'), 1)
        self.assertAlmostEqual(self.config.get_app_option_float('beta'), -2.2)
        self.assertListEqual(self.config.get_app_option_list('labels'),
            ['mon', 'wed', 'fri', '3.14'])
        self.assertTrue(self.config.get_boolean('Plugins', 'medfilter'))
        self.assertFalse(self.config.get_boolean('Plugins', 'normalize'))
        self.assertListEqual(self.config.get_list('Coordinates', 'app'), ['21', '-42'])
        self.assertEqual(self.config.get_int('Coordinates', 'alpha'), 1)
        self.assertAlmostEqual(self.config.get_float('Coordinates', 'beta'), -2.2)

    def test_has_option(self):
        """Verify has_option method returns True if option found,
        False otherwise."""
        self.write_cfg()
        self.assertTrue(self.config.has_app_option("path"))
        self.assertFalse(self.config.has_app_option("del_path"))
        self.config.set(section='Plugins', options={'medfilter':True,
                                                    'normalize':False})
        self.assertTrue(self.config.has_option("Plugins", "medfilter"))
        self.assertTrue(self.config.has_option("Plugins", "normalize"))
        self.assertFalse(self.config.has_option("Plugins", "meanfilter"))

    def test_bad_options(self):
        """Verify Configure instance returns None if options are not
        found or can't be converted"""
        self.write_cfg()
        self.assertIsNone(self.config.get_app_option_boolean('path'))
        self.assertIsNone(self.config.get_app_option_int('path'))
        self.assertIsNone(self.config.get_app_option_float('path'))
        self.assertIsNone(self.config.get_app_option_list('Potato'))
        self.assertIsNone(self.config.get('Plugins', "Colander"))

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

if __name__ == "__main__":
    unittest.main()