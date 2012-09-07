"""fetchplugin_dialog_model.py - model for the fetchplugin_dialog

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import plugin_installer
from models.mainmodel import get_logger

module_logger = get_logger(__name__)

class FetchPluginDialogModel(object):
    """Model for the FetchPluginDialog"""

    def __init__(self, controller):
        self.controller = controller
        self.plugin_fetcher = None
        module_logger.info("Successfully initialized FetchPluginDialogModel.")

    def get_plugin(self, url_dict):
        """Fetches the plugin"""
        plugin_url = url_dict.get('url')
        module_logger.info("Retrieving plugin from {0}".format(plugin_url))
        if url_dict.get('zip_encrypted', False):
            zip_password = url_dict.get('zip_password')
            module_logger.info("zip_password field is set")
        else:
            zip_password = None
            module_logger.info("zip_password field is set to None")
        self.plugin_fetcher = plugin_installer.PluginInstaller(plugin_url, zip_password)
        self.plugin_fetcher.fetch()

    def install_plugin(self):
        """Downloads, verifies, and installs the plugin.  Returns True if successful."""
        if self.plugin_fetcher is not None:
            return self.plugin_fetcher.install_plugin()
        module_logger.warning("Plugin installation failed.")
        return False

    def get_readme(self, url_dict):
        """Returns the plugin's README contents."""
        if self.plugin_fetcher is None:
            self.get_plugin(url_dict)
        return self.plugin_fetcher.retrieve_readme()


class FetchRemotePluginDialogModel(FetchPluginDialogModel):
    """Model for the FetchRemotePluginDialog"""

    def __init__(self, controller):
        self.controller = controller
        self.plugin_fetcher = None
        module_logger.info("Successfully initialized FetchRemotePluginDialogModel.")

    def get_plugin(self, url_dict):
        """Downloads the plugin"""
        plugin_url = url_dict.get('url')
        module_logger.info("Downloading plugin from {0}".format(plugin_url))
        if url_dict.get('login', False):
            username = url_dict.get('username')
            password = url_dict.get('password')
            module_logger.info("username and password fields set")
        else:
            username = None
            password = None
            module_logger.info("username and password fields set to None")
        if url_dict.get('zip_encrypted', False):
            zip_password = url_dict.get('zip_password')
            module_logger.info("zip_password field set")
        else:
            zip_password = None
            module_logger.info("zip_password field set to None")
        self.plugin_fetcher = plugin_installer.RemotePluginInstaller(plugin_url, username,
                                                                     password,
                                                                     zip_password)
        self.plugin_fetcher.fetch()