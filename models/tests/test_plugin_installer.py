"""test_plugin_installer.py - tests the plugin_installer module

Chris R. Coughlin (TRI/Austin, Inc.)
"""
from controllers import pathfinder

__author__ = 'Chris R. Coughlin'

import models.plugin_installer as plugin_installer
import models.zipper as zipper
import cStringIO
import unittest
import os
import random
import urllib
import SimpleHTTPServer
import SocketServer
import string
import threading

class TestPluginInstaller(unittest.TestCase):
    """Tests the LocalPluginInstaller class"""

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

    def setUp(self):
        self.good_plugin_installer = plugin_installer.PluginInstaller(self.good_plugin_loc)
        self.plugin_reader = zipper.UnZipper(self.good_plugin_loc)

    @property
    def good_plugin_loc(self):
        """Returns the full path to the known good plugin archive."""
        return TestPluginInstaller.local_plugin('good_medfilter_plugin.zip')

    @property
    def badfolders_plugin_loc(self):
        """Returns the full path to a known bad plugin (support folders must
        share name of the plugin archive)"""
        return TestPluginInstaller.local_plugin('badfolders_medfilter_plugin.zip')

    @property
    def badname_plugin_loc(self):
        """Returns the full path to a known bad plugin (root plugin module
        must share the name of the plugin archive)"""
        return TestPluginInstaller.local_plugin('badname_medfilter_plugin.zip')

    @property
    def badnomodule_plugin_loc(self):
        """Returns the full path to a known bad plugin (root plugin module
        must exist)"""
        return TestPluginInstaller.local_plugin('badnomodule_medfilter_plugin.zip')

    @property
    def badreadme_plugin_loc(self):
        """Returns the full path to a known bad plugin (plugin archive must
        have a properly-named README file)"""
        return TestPluginInstaller.local_plugin('badreadme_medfilter_plugin.zip')

    @property
    def badnoreadme_plugin_loc(self):
        """Returns the full path to a known bad plugin (plugin archive must
        have a README file)"""
        return TestPluginInstaller.local_plugin('badnoreadme_medfilter_plugin.zip')

    @property
    def badstructure_plugin_loc(self):
        """Returns the full path to a known bad plugin (plugin may only have
        a .py module and README file in the root)"""
        return TestPluginInstaller.local_plugin('badstructure_medfilter_plugin.zip')

    def test_init(self):
        """Verify correct initialization"""
        zip_pword = random.sample(string.ascii_letters, 9)
        a_plugin_fetcher = plugin_installer.PluginInstaller(self.good_plugin_loc,
                                                            zip_password=zip_pword)
        self.assertEqual(self.good_plugin_loc, a_plugin_fetcher.plugin_url)
        self.assertEqual(zip_pword, a_plugin_fetcher.zip_password)
        self.assertIsNone(a_plugin_fetcher.plugin)
        self.assertIsNone(a_plugin_fetcher.plugin_contents)

    def test_fetch(self):
        """Verify retrieval of the plugin archive"""
        a_plugin_fetcher = plugin_installer.PluginInstaller(self.good_plugin_loc)
        a_plugin_fetcher.fetch()
        with open(self.good_plugin_loc, 'rb') as fidin:
            local_plugin = fidin.read()
            self.assertEqual(local_plugin, a_plugin_fetcher.plugin)
            self.assertEqual(cStringIO.StringIO(local_plugin).getvalue(),
                             a_plugin_fetcher.plugin_contents.getvalue())

    def test_plugin_files(self):
        """Verify plugin_files method returns a list of files in the plugin archive"""
        expected_contents = self.plugin_reader.list_contents()
        self.good_plugin_installer.fetch()
        self.assertListEqual(expected_contents, self.good_plugin_installer.plugin_files)

    def test_readme_filenames(self):
        """Verify PluginInstaller maintains a list of acceptable root-level
        README filenames"""
        allowed_filenames = ['readme.txt', 'README.TXT', 'readme', 'README']
        self.assertListEqual(allowed_filenames, self.good_plugin_installer.readme_files)

    def test_retrieve_readme(self):
        """Verify retrieve_readme method returns contents of plugin's root-level
        README file"""
        self.good_plugin_installer.fetch()
        readme = None
        plugin_files = self.plugin_reader.list_contents()
        readme_filenames = ['readme.txt', 'README.TXT', 'readme', 'README']
        for readme_file in readme_filenames:
            if readme_file in plugin_files:
                readme = self.plugin_reader.read(readme_file)
        self.assertEqual(readme, self.good_plugin_installer.retrieve_readme())

    def test_verify_plugin_good(self):
        """Verify that verify_plugin method returns True if the plugin appears valid."""
        self.good_plugin_installer.fetch()
        self.assertTrue(self.good_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_folders(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named folders."""
        bad_plugin_installer = plugin_installer.PluginInstaller(self.badfolders_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_name(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named plugin module."""
        bad_plugin_installer = plugin_installer.PluginInstaller(self.badname_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_module(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named plugin module."""
        bad_plugin_installer = plugin_installer.PluginInstaller(self.badnomodule_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_readme(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named README."""
        bad_plugin_installer = plugin_installer.PluginInstaller(self.badreadme_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_noreadme(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to not having a README file in the root."""
        bad_plugin_installer = plugin_installer.PluginInstaller(self.badnoreadme_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_structure(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to having an invalid structure (support files in sub-folder; only module.py and
        README allowed in root)"""
        bad_plugin_installer = plugin_installer.PluginInstaller(self.badstructure_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_install_plugin(self):
        """Verify install_plugin method correctly installs a plugin; also
        verifies handling of encrypted ZIPs"""
        sample_plugin_url = TestPluginInstaller.local_plugin('greets_plugin.zip')
        installed_plugin_name = os.path.join(pathfinder.plugins_path(), 'greets_plugin.py')
        installer = plugin_installer.PluginInstaller(sample_plugin_url, zip_password='9225')
        installer.fetch()
        self.assertTrue(installer.verify_plugin())
        install_success = installer.install_plugin()
        self.assertTrue(os.path.exists(installed_plugin_name))
        self.assertTrue(install_success)
        # Clean up - attempt to remove the sample plugin if it already exists
        if os.path.exists(installed_plugin_name):
            try:
                os.remove(installed_plugin_name)
            except WindowsError: # file in use
                return


class TestRemotePluginInstaller(unittest.TestCase):
    """Tests the RemotePluginInstaller class"""

    @classmethod
    def setUpClass(cls):
        """Create a SimpleHTTPServer instance to serve test files from the support_files folder"""
        cls.PORT = 8000 + random.randint(1, 1000)
        req_handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        cls.httpd = SocketServer.TCPServer(("localhost", cls.PORT), req_handler)
        cls.httpd.timeout = 5
        cls.server_thd = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thd.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        if cls.server_thd.is_alive():
            cls.server_thd.join(1)

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
        return urllib.pathname2url(TestRemotePluginInstaller.local_plugin(plugin_name))

    @classmethod
    def plugin_url(cls, plugin_name):
        """Returns the URL to the specified plugin name when served by the test server"""
        return 'http://localhost:{0}/{1}'.format(cls.PORT,
                                                 TestRemotePluginInstaller.local_plugin_url(
                                                     plugin_name))

    @property
    def good_plugin(self):
        """Returns the path and filename to the known good plugin"""
        return TestRemotePluginInstaller.local_plugin('good_medfilter_plugin.zip')

    @property
    def good_plugin_url(self):
        """Returns the URL to the known good plugin"""
        return TestRemotePluginInstaller.plugin_url('good_medfilter_plugin.zip')

    @property
    def badfolders_plugin_url(self):
        """Returns the URL to a known bad plugin (support folders must
        share name of the plugin archive)"""
        return TestRemotePluginInstaller.plugin_url('badfolders_medfilter_plugin.zip')

    @property
    def badname_plugin_url(self):
        """Returns the URL to a known bad plugin (root plugin module
        must share the name of the plugin archive)"""
        return TestRemotePluginInstaller.plugin_url('badname_medfilter_plugin.zip')

    @property
    def badnomodule_plugin_url(self):
        """Returns the URL to a known bad plugin (root plugin module
        must exist)"""
        return TestRemotePluginInstaller.plugin_url('badnomodule_medfilter_plugin.zip')

    @property
    def badreadme_plugin_url(self):
        """Returns the URL to a known bad plugin (plugin archive must
        have a properly-named README file)"""
        return TestRemotePluginInstaller.plugin_url('badreadme_medfilter_plugin.zip')

    @property
    def badnoreadme_plugin_url(self):
        """Returns the URL to a known bad plugin (plugin archive must
        have a README file)"""
        return TestRemotePluginInstaller.plugin_url('badnoreadme_medfilter_plugin.zip')

    @property
    def badstructure_plugin_url(self):
        """Returns the URL to a known bad plugin (plugin may only have
        a .py module and README file in the root)"""
        return TestRemotePluginInstaller.plugin_url('badstructure_medfilter_plugin.zip')

    def setUp(self):
        """Creates a SimpleHTTPServer instance to handle a single
        request.  Use self.server_thd.start() to initiate."""
        #self.server_thd = threading.Thread(target=TestRemotePluginInstaller.httpd.handle_request)
        self.good_plugin_installer = plugin_installer.RemotePluginInstaller(self.good_plugin_url)
        self.plugin_reader = zipper.UnZipper(self.good_plugin)

    def test_init(self):
        """Verify correct initialization"""
        uname = random.sample(string.ascii_letters, 7)
        pword = random.sample(string.ascii_letters, 11)
        zip_pword = random.sample(string.ascii_letters, 9)
        a_plugin_fetcher = plugin_installer.RemotePluginInstaller(self.good_plugin_url,
                                                                  username=uname, password=pword,
                                                                  zip_password=zip_pword)
        self.assertEqual(self.good_plugin_url, a_plugin_fetcher.plugin_url)
        self.assertEqual(uname, a_plugin_fetcher.plugin_url_username)
        self.assertEqual(pword, a_plugin_fetcher.plugin_url_password)
        self.assertEqual(zip_pword, a_plugin_fetcher.zip_password)
        self.assertIsNone(a_plugin_fetcher.plugin)
        self.assertIsNone(a_plugin_fetcher.plugin_contents)

    def test_fetch(self):
        """Verify fetching a plugin"""
        self.good_plugin_installer.fetch()

    def test_plugin_files(self):
        """Verify plugin_files method returns a list of files in the plugin archive"""
        expected_contents = self.plugin_reader.list_contents()
        self.good_plugin_installer.fetch()
        self.assertListEqual(expected_contents, self.good_plugin_installer.plugin_files)

    def test_readme_filenames(self):
        """Verify PluginInstaller maintains a list of acceptable root-level
        README filenames"""
        allowed_filenames = ['readme.txt', 'README.TXT', 'readme', 'README']
        self.assertListEqual(allowed_filenames, self.good_plugin_installer.readme_files)

    def test_retrieve_readme(self):
        """Verify retrieve_readme method returns contents of plugin's root-level
        README file"""
        self.good_plugin_installer.fetch()
        readme = None
        plugin_files = self.plugin_reader.list_contents()
        readme_filenames = ['readme.txt', 'README.TXT', 'readme', 'README']
        for readme_file in readme_filenames:
            if readme_file in plugin_files:
                readme = self.plugin_reader.read(readme_file)
        self.assertEqual(readme, self.good_plugin_installer.retrieve_readme())

    def test_verify_plugin_good(self):
        """Verify that verify_plugin method returns True if the plugin appears valid."""
        self.good_plugin_installer.fetch()
        self.assertTrue(self.good_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_folders(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named folders."""
        bad_plugin_installer = plugin_installer.RemotePluginInstaller(self.badfolders_plugin_url)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_name(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named plugin module."""
        bad_plugin_installer = plugin_installer.RemotePluginInstaller(self.badname_plugin_url)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_module(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named plugin module."""
        bad_plugin_installer = plugin_installer.RemotePluginInstaller(self.badnomodule_plugin_url)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_readme(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named README."""
        bad_plugin_installer = plugin_installer.RemotePluginInstaller(self.badreadme_plugin_url)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_noreadme(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to not having a README file in the root."""
        bad_plugin_installer = plugin_installer.RemotePluginInstaller(self.badnoreadme_plugin_url)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_structure(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to having an invalid structure (support files in sub-folder; only module.py and
        README allowed in root)"""
        bad_plugin_installer = plugin_installer.RemotePluginInstaller(self.badstructure_plugin_url)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_install_plugin(self):
        """Verify install_plugin method correctly installs a plugin; also
        verifies handling of encrypted ZIPs"""
        sample_plugin_url = TestRemotePluginInstaller.plugin_url('greets_plugin.zip')
        installed_plugin_name = os.path.join(pathfinder.plugins_path(), 'greets_plugin.py')
        installer = plugin_installer.RemotePluginInstaller(sample_plugin_url, zip_password='9225')
        installer.fetch()
        self.assertTrue(installer.verify_plugin())
        install_success = installer.install_plugin()
        self.assertTrue(os.path.exists(installed_plugin_name))
        self.assertTrue(install_success)
        # Clean up - attempt to remove the sample plugin if it already exists
        if os.path.exists(installed_plugin_name):
            try:
                os.remove(installed_plugin_name)
            except WindowsError: # file in use
                return

if __name__ == "__main__":
    random.seed()
    unittest.main()