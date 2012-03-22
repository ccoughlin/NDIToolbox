"""plugin_installer.py - fetches and installs remote plugins

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
from models.fetcher import Fetcher
from models.zipper import UnZipper
import os.path
import cStringIO

class PluginInstaller(object):
    """Installs local plugin archives, supports global
    passwords on ZIPs."""

    def __init__(self, plugin_url, zip_password=None):
        self.plugin_url = plugin_url
        self.zip_password = zip_password
        self.plugin = None

    def fetch(self):
        """Retrieves the plugin, raising IOError if
        file not found."""
        with open(self.plugin_url, 'rb') as plugin_contents:
            self.plugin = plugin_contents.read()

    @property
    def plugin_contents(self):
        """Returns a cStringIO representation of the plugin,
        or None if no plugin has been loaded."""
        if self.plugin is not None:
            return cStringIO.StringIO(self.plugin)
        return None

    @property
    def plugin_files(self):
        """Returns a list of the files in the plugin archive"""
        files = []
        plugin_reader = UnZipper(self.plugin_contents, self.zip_password)
        if plugin_reader.is_ok():
            files = plugin_reader.list_contents()
        return files

    @property
    def readme_files(self):
        """Returns a list of acceptable root-level README file names"""
        return ['readme.txt', 'README.TXT', 'readme', 'README']

    def retrieve_readme(self):
        """Returns the contents of the plugin archive's root-level
        README, or None if not found."""
        readme_content = None
        if self.plugin is not None:
            readme_extractor = UnZipper(self.plugin_contents, self.zip_password)
            if readme_extractor.is_ok():
                plugin_files = readme_extractor.list_contents()
                for readme_file in self.readme_files:
                    if readme_file in plugin_files:
                        readme_content = readme_extractor.read(readme_file)
        return readme_content

    def verify_plugin(self):
        """Verify plugin conforms to basic plugin structure.  Returns
        True if the plugin appears ok, False otherwise."""
        plugin_ok = True
        if self.plugin is not None:
            plugin_zip = UnZipper(self.plugin_contents, self.zip_password)
            if not plugin_zip.is_ok():
                return False
            plugin_files = [each_file for each_file in plugin_zip.list_contents()]
            readme_found = False
            for valid_readme in self.readme_files:
                if valid_readme in plugin_files:
                    readme_found = True
                    break
            if not readme_found:
                return False
            zip_name = os.path.basename(self.plugin_url)
            zip_name_base, ext = os.path.splitext(zip_name)
            plugin_main = ''.join([zip_name_base, '.py'])
            if plugin_main not in plugin_files:
                return False
            plugin_fldr = zip_name_base
            support_files = [el for el in plugin_files if el not in self.readme_files and el != plugin_main]
            for each_file in support_files:
                install_fldr = os.path.dirname(each_file)
                if os.path.commonprefix([plugin_fldr, install_fldr]) != plugin_fldr:
                    return False
        return plugin_ok

    def install_plugin(self):
        """Installs the plugin in the default plugin path.
        Returns True if installation succeeded."""
        plugin_path = pathfinder.plugins_path()
        if self.plugin is not None:
            plugin_zip = UnZipper(self.plugin_contents, self.zip_password)
            if self.verify_plugin():
                plugin_files = [each_file for each_file in plugin_zip.list_contents() if
                                each_file not in self.readme_files]
                for each_file in plugin_files:
                    plugin_zip.extract(each_file, plugin_path)
                    if not os.path.exists(os.path.join(plugin_path, each_file)):
                        return False
            else:
                return False
        else:
            return False
        return True


class RemotePluginInstaller(PluginInstaller):
    """Fetches and installs remote plugins.  Supports
    HTTP Basic Auth and global passwords on ZIP archives."""

    def __init__(self, plugin_url, username=None, password=None, zip_password=None):
        self.plugin_url = plugin_url
        self.plugin_url_username = username
        self.plugin_url_password = password
        self.zip_password = zip_password
        self.plugin = None

    def fetch(self):
        """Retrieves the remote plugin, raising IOError if
        file not found / server unavailable."""
        plugin_fetcher = Fetcher(self.plugin_url, self.plugin_url_username, self.plugin_url_password)
        self.plugin = plugin_fetcher.fetch()