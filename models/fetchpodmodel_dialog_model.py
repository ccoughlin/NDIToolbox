"""fetchpodmodel_dialog_model.py - models for the FetchPODModelDialogs

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import fetchplugin_dialog_model as fetchplugin_model
from models import podmodel_installer

class FetchPODModelDialogModel(fetchplugin_model.FetchPluginDialogModel):
    """Model for the FetchPODModelDialog"""

    def __init__(self, controller):
        super(FetchPODModelDialogModel, self).__init__(controller)

    def get_plugin(self, url_dict):
        """Fetches the plugin"""
        plugin_url = url_dict.get('url')
        if url_dict.get('zip_encrypted', False):
            zip_password = url_dict.get('zip_password')
        else:
            zip_password = None
        self.plugin_fetcher = podmodel_installer.PODModelInstaller(plugin_url, zip_password)
        self.plugin_fetcher.fetch()


class FetchRemotePODModelDialogModel(fetchplugin_model.FetchRemotePluginDialogModel):
    """Model for the FetchRemotePODModelDialog"""

    def __init__(self, controller):
        super(FetchRemotePODModelDialogModel, self).__init__(controller)

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
        self.plugin_fetcher = podmodel_installer.RemotePODModelInstaller(plugin_url, username,
                                                                         password, zip_password)
        self.plugin_fetcher.fetch()