"""podmodel_installer.py - fetches and installs POD Models

Chris R. Coughlin (TRI/Austin, Inc.)
"""

from controllers import pathfinder
from models import plugin_installer
from models.fetcher import Fetcher
from models.zipper import UnZipper
from models.mainmodel import get_logger
import os.path

module_logger = get_logger(__name__)

class PODModelInstaller(plugin_installer.PluginInstaller):
    """Subclass of PluginInstaller:  installs local POD Model archives, supports global
    passwords on ZIPs."""

    def __init__(self, plugin_url, zip_password=None):
        super(PODModelInstaller, self).__init__(plugin_url, zip_password)
        module_logger.info("Successfully initialized PODModelInstaller.")

    def verify_plugin(self):
        """Verify plugin conforms to basic plugin structure.  Returns
        True if the plugin appears ok, False otherwise."""
        plugin_ok = True
        if self.plugin is not None:
            plugin_zip = UnZipper(self.plugin_contents, self.zip_password)
            if not plugin_zip.is_ok():
                module_logger.warning("Plugin archive corrupted - failed CRC check.")
                return False
            plugin_files = [each_file for each_file in plugin_zip.list_contents()]
            readme_found = False
            for valid_readme in self.readme_files:
                if valid_readme in plugin_files:
                    readme_found = True
                    break
            if not readme_found:
                module_logger.warning("Plugin does not conform to spec - no README file found.")
                return False
            zip_name = os.path.basename(self.plugin_url)
            zip_name_base, ext = os.path.splitext(zip_name)
            plugin_main = ''.join([zip_name_base, '.py'])
            plugin_cfg = ''.join([zip_name_base, '.cfg'])
            if plugin_main not in plugin_files:
                module_logger.warning("Plugin does not conform to spec - no main Python file found.")
                return False
            plugin_fldr = zip_name_base
            support_files = [el for el in plugin_files if
                             el not in self.readme_files and el != plugin_main
                             and el != plugin_cfg]
            for each_file in support_files:
                install_fldr = os.path.dirname(each_file)
                if os.path.commonprefix([plugin_fldr, install_fldr]) != plugin_fldr:
                    module_logger.warning("Plugin does not conform to spec - incorrect folder structure.")
                    return False
        return plugin_ok

    def install_plugin(self):
        """Installs the plugin in the default plugin path.
        Returns True if installation succeeded."""
        plugin_path = pathfinder.podmodels_path()
        if self.plugin is not None:
            plugin_zip = UnZipper(self.plugin_contents, self.zip_password)
            if self.verify_plugin():
                plugin_files = [each_file for each_file in plugin_zip.list_contents() if
                                each_file not in self.readme_files]
                for each_file in plugin_files:
                    plugin_zip.extract(each_file, plugin_path)
                    if not os.path.exists(os.path.join(plugin_path, each_file)):
                        module_logger.warning("Plugin installation failed.")
                        return False
            else:
                module_logger.warning("Plugin installation failed - plugin does not conform to spec.")
                return False
        else:
            module_logger.warning("Plugin installation failed - plugin is not set.")
            return False
        return True


class RemotePODModelInstaller(PODModelInstaller):
    """Fetches and installs remote POD models.  Supports
    HTTP Basic Auth and global passwords on ZIP archives."""

    def __init__(self, plugin_url, username=None, password=None, zip_password=None):
        self.plugin_url = plugin_url
        self.plugin_url_username = username
        self.plugin_url_password = password
        self.zip_password = zip_password
        self.plugin = None
        module_logger.info("Successfully initialized RemotePODModelInstaller.")

    def fetch(self):
        """Retrieves the remote plugin, raising IOError if
        file not found / server unavailable."""
        plugin_fetcher = Fetcher(self.plugin_url, self.plugin_url_username,
                                 self.plugin_url_password)
        self.plugin = plugin_fetcher.fetch()