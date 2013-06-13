"""fetchplugin_dialog_ctrl.py - controller for the fetchplugin_dialog

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import fetchplugin_dialog_model
from models import workerthread
from models.mainmodel import get_logger
from views import dialogs
import wx
import Queue

module_logger = get_logger(__name__)

class FetchPluginDialogController(object):
    """Controller for the FetchPluginDialog"""

    def __init__(self, view):
        self.view = view
        self.model = fetchplugin_dialog_model.FetchPluginDialogModel(self)
        self.init_url()
        module_logger.info("FetchPluginDialogController successfully created.")

    def init_url(self):
        """Initializes URL, username, and password(s) to None"""
        plugin_url = {'url': None,
                      'zip_encrypted': False,
                      'zip_password': None}
        return plugin_url

    def get_configured_url(self):
        """Configures the URL, username, and password(s) for downloading the plugin, and returns
        the result as a dict."""
        plugin_url = self.init_url()
        plugin_url['url'] = self.view.url_tc.GetValue()
        plugin_url['zip_encrypted'] = self.view.encryptedzip_cb.IsChecked()
        if self.view.encryptedzip_cb.IsChecked():
            plugin_url['zip_password'] = self.view.zippword_tc.GetValue()
        else:
            plugin_url['zip_password'] = None
        return plugin_url

    def fetch_plugin(self):
        """Downloads the plugin"""
        url_dict = self.get_configured_url()
        busy_dlg = dialogs.progressDialog(dlg_title="Retrieving Archive",
                                          dlg_msg="Please wait, retrieving archive...")
        exception_queue = Queue.Queue()
        fetch_plugin_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                                     target=self.model.get_plugin,
                                                     args=(url_dict,))
        fetch_plugin_thd.start()
        while True:
            fetch_plugin_thd.join(0.125)
            busy_dlg.update()
            if not fetch_plugin_thd.is_alive():
                busy_dlg.close()
                try:
                    exc_type, exc = exception_queue.get(block=False)
                    err_str = str(exc)
                    if len(err_str) == 0:
                        err_str = exc_type.__name__
                    module_logger.error("Unable to read archive: {0}".format(err_str))
                    err_msg = "An error occurred while reading the archive:\n{0}".format(err_str)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Read Archive",
                                               style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                except Queue.Empty:
                    pass
                break
            wx.GetApp().Yield()

    def install_plugin(self):
        """Downloads, verifies, and installs the plugin"""
        try:
            self.fetch_plugin()
            if not self.model.install_plugin():
                err_dlg = wx.MessageDialog(self.view, message="Plugin installation failed.",
                                           caption="Unable To Install Plugin", style=wx.ICON_ERROR)
                module_logger.error("Failed to install plugin.")
                err_dlg.ShowModal()
                err_dlg.Destroy()
            else:
                success_dlg = wx.MessageDialog(self.view, message="Plugin installation successful"\
                                                                  ".",
                                               caption="Installation Complete",
                                               style=wx.ICON_INFORMATION)
                module_logger.info("Plugin installation successful.")
                success_dlg.ShowModal()
                success_dlg.Destroy()
        except Exception as err:
            module_logger.error("Failed to install plugin: {0}".format(err))
            err_msg = "{0}".format(err)
            if err_msg == "":
                err_msg = "An error occurred during the installation process."
            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                       caption="Unable To Install Plugin", style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    # Event Handlers
    def on_about_plugin(self, evt):
        """Handles the request to retrieve info about the plugin"""
        busy_dlg = dialogs.progressDialog(dlg_title="Retrieving Archive",
                                          dlg_msg="Please wait, retrieving archive...")
        try:
            self.fetch_plugin()
            readme = self.model.get_readme(self.get_configured_url())
            text_display_dlg = dialogs.TextDisplayDialog(parent=self.view, text=readme,
                                                         title='README',
                                                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
            text_display_dlg.Show()
        except Exception as err:
            module_logger.error("Failed to retrieve plugin README: {0}".format(err))
            err_msg = "{0}".format(err)
            if err_msg == "":
                err_msg = "An error occurred attempting to retrieve the archive's README file."
            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                       caption="Unable To Retrieve README", style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()
        finally:
            busy_dlg.close()


class FetchRemotePluginDialogController(FetchPluginDialogController):
    """Controller for the FetchRemotePluginDialog"""

    def __init__(self, view):
        self.view = view
        self.model = fetchplugin_dialog_model.FetchRemotePluginDialogModel(self)
        self.init_url()
        module_logger.info("FetchRemotePluginDialogController successfully created.")

    def init_url(self):
        """Initializes URL, username, and password(s) to None"""
        plugin_url = {'url': None,
                      'login': False,
                      'username': None,
                      'password': None,
                      'zip_encrypted': False,
                      'zip_password': None}
        return plugin_url

    def get_configured_url(self):
        """Configures the URL, username, and password(s) for downloading the plugin, and returns
        the result as a dict."""
        plugin_url = self.init_url()
        plugin_url['url'] = self.view.url_tc.GetValue()
        plugin_url['login'] = self.view.login_cb.IsChecked()
        if self.view.login_cb.IsChecked():
            plugin_url['username'] = self.view.uname_tc.GetValue()
            plugin_url['password'] = self.view.pword_tc.GetValue()
        else:
            plugin_url['username'] = None
            plugin_url['password'] = None
        plugin_url['zip_encrypted'] = self.view.encryptedzip_cb.IsChecked()
        if self.view.encryptedzip_cb.IsChecked():
            plugin_url['zip_password'] = self.view.zippword_tc.GetValue()
        else:
            plugin_url['zip_password'] = None
        return plugin_url
