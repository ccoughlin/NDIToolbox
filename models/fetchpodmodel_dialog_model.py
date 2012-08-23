"""fetchpodmodel_dialog_model.py - models for the FetchPODModelDialogs

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import fetchplugin_dialog_model as fetchplugin_model
from models import podmodel_installer
from models.mainmodel import get_logger

module_logger = get_logger(__name__)

class FetchPODModelDialogModel(fetchplugin_model.FetchPluginDialogModel):
    """Model for the FetchPODModelDialog"""

    def __init__(self, controller):
        super(FetchPODModelDialogModel, self).__init__(controller)
        module_logger.info("Successfully initialized FetchPODModelDialogModel")

    def get_plugin(self, url_dict):
        """Fetches the plugin"""
        plugin_url = url_dict.get('url')
        module_logger.info("Attempting to fetch POD Model from {0}".format(plugin_url))
        if url_dict.get('zip_encrypted', False):
            zip_password = url_dict.get('zip_password')
            module_logger.info("zip_password field has been set")
        else:
            zip_password = None
            module_logger.info("zip_password field has been set to None")
        self.plugin_fetcher = podmodel_installer.PODModelInstaller(plugin_url, zip_password)
        self.plugin_fetcher.fetch()


class FetchRemotePODModelDialogModel(fetchplugin_model.FetchRemotePluginDialogModel):
    """Model for the FetchRemotePODModelDialog"""

    def __init__(self, controller):
        super(FetchRemotePODModelDialogModel, self).__init__(controller)
        module_logger.info("Successfully initialized FetchremotePODModelDialogModel.")

    def get_plugin(self, url_dict):
        """Downloads the plugin"""
        plugin_url = url_dict.get('url')
        module_logger.info("Attempting to fetch POD Model from {0}".format(plugin_url))
        if url_dict.get('login', False):
            username = url_dict.get('username')
            password = url_dict.get('password')
            module_logger.info("username and password fields are set")
        else:
            username = None
            password = None
            module_logger.info("username and password fields are set to None")
        if url_dict.get('zip_encrypted', False):
            zip_password = url_dict.get('zip_password')
            module_logger.info("zip_password field is set")
        else:
            zip_password = None
            module_logger.info("zip_password field is set to None")
        self.plugin_fetcher = podmodel_installer.RemotePODModelInstaller(plugin_url, username,
                                                                         password, zip_password)
        self.plugin_fetcher.fetch()