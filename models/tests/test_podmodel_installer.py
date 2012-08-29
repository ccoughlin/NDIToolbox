"""test_podmodel_installer.py - tests the podmodel_installer module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
from models.tests import test_plugin_installer
import models.podmodel_installer as podmodel_installer
import models.zipper as zipper
import cStringIO
import unittest
import os
import random
import string
import threading

class TestPODModelInstaller(test_plugin_installer.TestPluginInstaller):
    """Tests the PODModelInstaller class"""

    def setUp(self):
        self.good_plugin_installer = podmodel_installer.PODModelInstaller(self.good_plugin_loc)
        self.plugin_reader = zipper.UnZipper(self.good_plugin_loc)

    @property
    def good_plugin_loc(self):
        """Returns the full path to the known good plugin archive."""
        return test_plugin_installer.TestPluginInstaller.local_plugin('good_podmodel.zip')

    @property
    def badfolders_plugin_loc(self):
        """Returns the full path to a known bad plugin (support folders must
        share name of the plugin archive)"""
        return test_plugin_installer.TestPluginInstaller.local_plugin('badfolders_podmodel.zip')

    @property
    def badname_plugin_loc(self):
        """Returns the full path to a known bad plugin (root plugin module
        must share the name of the plugin archive)"""
        return test_plugin_installer.TestPluginInstaller.local_plugin('badname_podmodel.zip')

    @property
    def badnomodule_plugin_loc(self):
        """Returns the full path to a known bad plugin (root plugin module
        must exist)"""
        return test_plugin_installer.TestPluginInstaller.local_plugin('badnomodule_podmodel.zip')

    @property
    def badreadme_plugin_loc(self):
        """Returns the full path to a known bad plugin (plugin archive must
        have a properly-named README file)"""
        return test_plugin_installer.TestPluginInstaller.local_plugin('badreadme_podmodel.zip')

    @property
    def badnoreadme_plugin_loc(self):
        """Returns the full path to a known bad plugin (plugin archive must
        have a README file)"""
        return test_plugin_installer.TestPluginInstaller.local_plugin('badnoreadme_podmodel.zip')

    @property
    def badstructure_plugin_loc(self):
        """Returns the full path to a known bad plugin (plugin may only have
        a .py module and README file in the root)"""
        return test_plugin_installer.TestPluginInstaller.local_plugin('badstructure_podmodel.zip')

    def test_init(self):
        """Verify correct initialization"""
        zip_pword = random.sample(string.ascii_letters, 9)
        a_plugin_fetcher = podmodel_installer.PODModelInstaller(self.good_plugin_loc,
                                                                zip_password=zip_pword)
        self.assertEqual(self.good_plugin_loc, a_plugin_fetcher.plugin_url)
        self.assertEqual(zip_pword, a_plugin_fetcher.zip_password)
        self.assertIsNone(a_plugin_fetcher.plugin)
        self.assertIsNone(a_plugin_fetcher.plugin_contents)

    def test_fetch(self):
        """Verify retrieval of the plugin archive"""
        a_plugin_fetcher = podmodel_installer.PODModelInstaller(self.good_plugin_loc)
        a_plugin_fetcher.fetch()
        with open(self.good_plugin_loc, 'rb') as fidin:
            local_plugin = fidin.read()
            self.assertEqual(local_plugin, a_plugin_fetcher.plugin)
            self.assertEqual(cStringIO.StringIO(local_plugin).getvalue(),
                             a_plugin_fetcher.plugin_contents.getvalue())

    def test_verify_plugin_bad_folders(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named folders."""
        bad_plugin_installer = podmodel_installer.PODModelInstaller(self.badfolders_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_name(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named plugin module."""
        bad_plugin_installer = podmodel_installer.PODModelInstaller(self.badname_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_module(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named plugin module."""
        bad_plugin_installer = podmodel_installer.PODModelInstaller(self.badnomodule_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_readme(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to improperly-named README."""
        bad_plugin_installer = podmodel_installer.PODModelInstaller(self.badreadme_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_noreadme(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to not having a README file in the root."""
        bad_plugin_installer = podmodel_installer.PODModelInstaller(self.badnoreadme_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_verify_plugin_bad_structure(self):
        """Verify that verify_plugin method returns False if the plugin appears invalid due
        to having an invalid structure (support files in sub-folder; only module.py and
        README allowed in root)"""
        bad_plugin_installer = podmodel_installer.PODModelInstaller(self.badstructure_plugin_loc)
        bad_plugin_installer.fetch()
        self.assertFalse(bad_plugin_installer.verify_plugin())

    def test_install_plugin(self):
        """Verify install_plugin method correctly installs a plugin; also
        verifies handling of encrypted ZIPs"""
        sample_plugin_url = TestPODModelInstaller.local_plugin('good_podmodel.zip')
        installed_plugin_name = os.path.join(pathfinder.podmodels_path(), 'good_podmodel.py')
        installer = podmodel_installer.PODModelInstaller(sample_plugin_url)
        installer.fetch()
        self.assertTrue(installer.verify_plugin())
        install_success = installer.install_plugin()
        self.assertTrue(os.path.exists(installed_plugin_name))
        self.assertTrue(install_success)
        # Clean up - attempt to remove the sample POD Model if it already exists
        podmodel_files = zipper.UnZipper(sample_plugin_url).list_contents()
        for each_file in podmodel_files:
            full_path = os.path.join(pathfinder.podmodels_path(), each_file)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except WindowsError: # file in use
                    return


class TestRemotePODModelInstaller(test_plugin_installer.TestRemotePluginInstaller):
    """Tests the RemotePODModelInstaller class"""

    @property
    def good_plugin(self):
        """Returns the path and filename to the known good plugin"""
        return TestRemotePODModelInstaller.local_plugin('good_podmodel.zip')

    @property
    def good_plugin_url(self):
        """Returns the URL to the known good plugin"""
        return TestRemotePODModelInstaller.plugin_url('good_podmodel.zip')

    @property
    def badfolders_plugin_url(self):
        """Returns the URL to a known bad plugin (support folders must
        share name of the plugin archive)"""
        return TestRemotePODModelInstaller.plugin_url('badfolders_podmodel.zip')

    @property
    def badname_plugin_url(self):
        """Returns the URL to a known bad plugin (root plugin module
        must share the name of the plugin archive)"""
        return TestRemotePODModelInstaller.plugin_url('badname_podmodel.zip')

    @property
    def badnomodule_plugin_url(self):
        """Returns the URL to a known bad plugin (root plugin module
        must exist)"""
        return TestRemotePODModelInstaller.plugin_url('badnomodule_podmodel.zip')

    @property
    def badreadme_plugin_url(self):
        """Returns the URL to a known bad plugin (plugin archive must
        have a properly-named README file)"""
        return TestRemotePODModelInstaller.plugin_url('badreadme_podmodel.zip')

    @property
    def badnoreadme_plugin_url(self):
        """Returns the URL to a known bad plugin (plugin archive must
        have a README file)"""
        return TestRemotePODModelInstaller.plugin_url('badnoreadme_podmodel.zip')

    @property
    def badstructure_plugin_url(self):
        """Returns the URL to a known bad plugin (plugin may only have
        a .py module and README file in the root)"""
        return TestRemotePODModelInstaller.plugin_url('badstructure_podmodel.zip')

    def setUp(self):
        """Creates a SimpleHTTPServer instance to handle a single
        request.  Use self.server_thd.start() to initiate."""
        #self.server_thd = threading.Thread(target=TestRemotePluginInstaller.httpd.handle_request)
        self.good_plugin_installer = podmodel_installer.RemotePODModelInstaller(self.good_plugin_url)
        self.plugin_reader = zipper.UnZipper(self.good_plugin)

    def test_init(self):
        """Verify correct initialization"""
        uname = random.sample(string.ascii_letters, 7)
        pword = random.sample(string.ascii_letters, 11)
        zip_pword = random.sample(string.ascii_letters, 9)
        a_plugin_fetcher = podmodel_installer.RemotePODModelInstaller(self.good_plugin_url,
                                                                      username=uname,
                                                                      password=pword
                                                                      , zip_password=zip_pword)
        self.assertEqual(self.good_plugin_url, a_plugin_fetcher.plugin_url)
        self.assertEqual(uname, a_plugin_fetcher.plugin_url_username)
        self.assertEqual(pword, a_plugin_fetcher.plugin_url_password)
        self.assertEqual(zip_pword, a_plugin_fetcher.zip_password)
        self.assertIsNone(a_plugin_fetcher.plugin)
        self.assertIsNone(a_plugin_fetcher.plugin_contents)

    def test_fetch(self):
        """Verify fetching a plugin"""
        self.good_plugin_installer.fetch()
        with open(self.good_plugin, 'rb') as fidin:
            local_plugin = fidin.read()
            self.assertEqual(local_plugin, self.good_plugin_installer.plugin)
            self.assertEqual(cStringIO.StringIO(local_plugin).getvalue(),
                             self.good_plugin_installer.plugin_contents.getvalue())

    def test_install_plugin(self):
        """Verify install_plugin method correctly installs a plugin; also
        verifies handling of encrypted ZIPs"""
        sample_plugin_url = TestRemotePODModelInstaller.plugin_url('good_podmodel.zip')
        installed_plugin_name = os.path.join(pathfinder.podmodels_path(), 'good_podmodel.py')
        installer = podmodel_installer.RemotePODModelInstaller(sample_plugin_url)
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
    unittest.main()