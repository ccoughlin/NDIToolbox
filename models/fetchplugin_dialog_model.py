"""fetchplugin_dialog_model.py - model for the fetchplugin_dialog

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import plugin_installer

class FetchPluginDialogModel(object):
    """Model for the FetchPluginDialog"""
    # TODO - beef up exception handling

    def __init__(self, controller):
        self.controller = controller
        self.plugin_fetcher = None

    def get_plugin(self, url_dict):
        """Downloads the plugin"""
        plugin_url = url_dict.get('url')
        if url_dict.get('login', False):
            username = url_dict.get('username')
            password = url_dict.get('password')
        else:
            username = None
            password = None
        if url_dict.get('zip_encrypted', False):
            zip_password = url_dict.get('zip_password')
        else:
            zip_password = None
        self.plugin_fetcher = plugin_installer.PluginInstaller(plugin_url, username, password, zip_password)
        self.plugin_fetcher.fetch()

    def install_plugin(self):
        """Downloads, verifies, and installs the plugin.  Returns True if successful."""
        if self.plugin_fetcher is not None:
            return self.plugin_fetcher.install_plugin()
        return False

    def get_readme(self, url_dict):
        """Returns the plugin's README contents."""
        if self.plugin_fetcher is not None:
            return self.plugin_fetcher.retrieve_readme()