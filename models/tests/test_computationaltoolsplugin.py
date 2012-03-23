"""test_computationaltoolsplugin.py - tests the computationaltoolsplugin module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.abstractplugin import ComputationalToolsPlugin
import unittest

class TestComputationalToolsPlugin(unittest.TestCase):
    """Tests the ComputationalToolsPlugin class"""

    def setUp(self):
        self.plugin_name = "Test Plugin"
        self.plugin_description = "Unit test of TRI Plugin template"
        self.plugin = ComputationalToolsPlugin(name=self.plugin_name,
                                               description=self.plugin_description)

    def test_init(self):
        """Verify successful instantiation"""
        self.assertTrue(isinstance(self.plugin, ComputationalToolsPlugin))
        self.assertEqual(self.plugin.name, self.plugin_name)
        self.assertEqual(self.plugin.description, self.plugin_description)
        self.assertTrue(hasattr(self.plugin, "_data"))
        self.assertTrue(hasattr(self.plugin, "data"))
        self.assertTrue(hasattr(self.plugin, "run"))

if __name__ == "__main__":
    unittest.main()