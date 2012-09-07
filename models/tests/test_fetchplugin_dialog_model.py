"""test_fetchplugin_dialog_model.py - tests the fetchplugin_dialog_model module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import fetchplugin_dialog_model
from models import zipper
from controllers import pathfinder
import cStringIO
import os
import SimpleHTTPServer
import SocketServer
import random
import threading
import unittest
import urllib

class TestFetchPluginDialogModel(unittest.TestCase):
    """Tests the FetchPluginDialogModel class"""

    @classmethod
    def local_plugin(cls, plugin_name):
        """Returns the local path and filename of the specified plugin archive."""
        cur_dir = os.getcwd()
        if os.path.normcase(cur_dir) == os.path.normcase(os.path.dirname(__file__)):
            # Running this test module directly
            return os.path.join('support_files', plugin_name)
        else:
            # Running as part of larger project test suite
            return os.path.join('models', 'tests', 'support_files', plugin_name)

    @property
    def plugin(self):
        """Returns the path and filename to the known good plugin"""
        return TestFetchPluginDialogModel.local_plugin('good_medfilter_plugin.zip')

    def setUp(self):
        """Creates a SimpleHTTPServer instance to handle a single
        request.  Use self.server_thd.start() to initiate."""
        self.mock_controller = ""
        self.model = fetchplugin_dialog_model.FetchPluginDialogModel(self.mock_controller)
        self.plugin_url_params = {'url': self.plugin,
                                  'zip_encrypted': False,
                                  'zip_password': None}

    def test_get_plugin(self):
        """Verify the model successfully retrieves the plugin"""
        self.model.get_plugin(self.plugin_url_params)
        with open(self.plugin, 'rb') as fidin:
            local_plugin = fidin.read()
            self.assertEqual(local_plugin, self.model.plugin_fetcher.plugin)
            self.assertEqual(cStringIO.StringIO(local_plugin).getvalue(),
                             self.model.plugin_fetcher.plugin)

    def test_get_readme(self):
        """Verify model returns the plugin archive's README"""
        readme_fetcher = zipper.UnZipper(self.plugin)
        expected_readme = readme_fetcher.read("readme.txt")
        retrieved_readme = self.model.get_readme(self.plugin_url_params)
        self.assertEqual(expected_readme, retrieved_readme)

    def test_install_plugin(self):
        """Verify installation of the plugin"""
        sample_plugin_url = TestFetchPluginDialogModel.local_plugin('greets_plugin.zip')
        installed_plugin_name = os.path.join(pathfinder.plugins_path(), 'greets_plugin.py')
        plugin_url_params = {'url': sample_plugin_url,
                             'zip_encrypted': True,
                             'zip_password': '9225'}
        self.model.get_plugin(plugin_url_params)
        successful_installation = self.model.install_plugin()
        self.assertTrue(os.path.exists(installed_plugin_name))
        self.assertTrue(successful_installation)
        # Clean up - attempt to remove the sample plugin if it already exists
        if os.path.exists(installed_plugin_name):
            try:
                os.remove(installed_plugin_name)
            except WindowsError: # file in use
                return


class TestRemoteFetchPluginDialogModel(unittest.TestCase):
    """Tests the FetchRemotePluginDialogModel class"""

    @classmethod
    def setUpClass(cls):
        """Create a SimpleHTTPServer instance to serve test files from the support_files folder"""
        cls.PORT = 8000 + random.randint(1, 1000)
        req_handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        cls.httpd = SocketServer.TCPServer(("localhost", cls.PORT), req_handler)
        cls.httpd.timeout = 5

    @classmethod
    def local_plugin(cls, plugin_name):
        """Returns the local path and filename of the specified plugin archive."""
        cur_dir = os.getcwd()
        if os.path.normcase(cur_dir) == os.path.normcase(os.path.dirname(__file__)):
            # Running this test module directly
            return os.path.join('support_files', plugin_name)
        else:
            # Running as part of larger project test suite
            return os.path.join('models', 'tests', 'support_files', plugin_name)

    @classmethod
    def local_plugin_url(cls, plugin_name):
        """Returns the plugin converted to an URL"""
        return urllib.pathname2url(TestRemoteFetchPluginDialogModel.local_plugin(plugin_name))

    @classmethod
    def plugin_url_params(cls, plugin_name):
        """Returns the URL to the specified plugin name when served by the test server"""
        return 'http://localhost:{0}/{1}'.format(cls.PORT,
                                                 TestRemoteFetchPluginDialogModel.local_plugin_url(
                                                     plugin_name))

    @property
    def plugin(self):
        """Returns the path and filename to the known good plugin"""
        return TestRemoteFetchPluginDialogModel.local_plugin('good_medfilter_plugin.zip')

    @property
    def good_plugin_url(self):
        """Returns the URL to the known good plugin"""
        return TestRemoteFetchPluginDialogModel.plugin_url_params('good_medfilter_plugin.zip')

    def setUp(self):
        """Creates a SimpleHTTPServer instance to handle a single
        request.  Use self.server_thd.start() to initiate."""
        self.server_thd = threading.Thread(
            target=TestRemoteFetchPluginDialogModel.httpd.handle_request)
        self.mock_controller = ""
        self.model = fetchplugin_dialog_model.FetchRemotePluginDialogModel(self.mock_controller)
        self.plugin_url_params = {'url': self.good_plugin_url,
                                  'login': False,
                                  'username': None,
                                  'password': None,
                                  'zip_encrypted': False,
                                  'zip_password': None}

    def tearDown(self):
        """Shuts down the server process if still active"""
        if self.server_thd.is_alive():
            self.server_thd.join()

    def test_get_plugin(self):
        """Verify the model successfully retrieves the plugin"""
        self.server_thd.start()
        self.model.get_plugin(self.plugin_url_params)
        with open(self.plugin, 'rb') as fidin:
            local_plugin = fidin.read()
            self.assertEqual(local_plugin, self.model.plugin_fetcher.plugin)
            self.assertEqual(cStringIO.StringIO(local_plugin).getvalue(),
                             self.model.plugin_fetcher.plugin)

    def test_get_readme(self):
        """Verify model returns the plugin archive's README"""
        self.server_thd.start()
        readme_fetcher = zipper.UnZipper(self.plugin)
        expected_readme = readme_fetcher.read("readme.txt")
        self.model.get_plugin(self.plugin_url_params)
        retrieved_readme = self.model.get_readme(self.plugin_url_params)
        self.assertEqual(expected_readme, retrieved_readme)

    def test_install_plugin(self):
        """Verify installation of the plugin"""
        self.server_thd.start()
        sample_plugin_url = TestRemoteFetchPluginDialogModel.plugin_url_params('greets_plugin.zip')
        installed_plugin_name = os.path.join(pathfinder.plugins_path(), 'greets_plugin.py')
        plugin_url_params = {'url': sample_plugin_url,
                             'login': False,
                             'username': None,
                             'password': None,
                             'zip_encrypted': True,
                             'zip_password': '9225'}
        self.model.get_plugin(plugin_url_params)
        successful_installation = self.model.install_plugin()
        self.assertTrue(os.path.exists(installed_plugin_name))
        self.assertTrue(successful_installation)
        # Clean up - attempt to remove the sample plugin if it already exists
        if os.path.exists(installed_plugin_name):
            try:
                os.remove(installed_plugin_name)
            except WindowsError: # file in use
                return

if __name__ == "__main__":
    random.seed()
    unittest.main()