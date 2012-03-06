"""fetchplugin_dialog_ctrl.py - controller for the fetchplugin_dialog

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import fetchplugin_dialog_model
from views import dialogs
import wx
import threading

class FetchPluginDialogController(object):
    """Controller for the FetchPluginDialog"""
    # TODO - beef up exception handling

    def __init__(self, view):
        self.view = view
        self.model = fetchplugin_dialog_model.FetchPluginDialogModel(self)
        self.init_url()

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

    def fetch_plugin(self):
        """Downloads the plugin"""
        url_dict = self.get_configured_url()
        fetch_plugin_thd = threading.Thread(target=self.model.get_plugin, args=(url_dict,))
        fetch_plugin_thd.setDaemon(True)
        fetch_plugin_thd.start()
        while True:
            fetch_plugin_thd.join(0.125)
            if not fetch_plugin_thd.is_alive():
                break
            wx.GetApp().Yield()

    def install_plugin(self):
        """Downloads, verifies, and installs the plugin"""
        busy_dlg = dialogs.progressDialog(dlg_title="Retrieving Plugin",
            dlg_msg="Please wait, downloading plugin...")
        try:
            self.fetch_plugin()
            if not self.model.install_plugin():
                err_dlg = wx.MessageDialog(self.view, message="Plugin installation failed.",
                    caption="Unable To Install Plugin", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
            else:
                success_dlg = wx.MessageDialog(self.view, message="Plugin installation successful.",
                    caption="Installation Complete", style=wx.ICON_INFORMATION)
                success_dlg.ShowModal()
                success_dlg.Destroy()
        except Exception as err:
            err_msg = "{0}".format(err)
            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                caption="Unable To Install Plugin", style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()
        finally:
            busy_dlg.close()

    # Event Handlers
    def on_about_plugin(self, evt):
        """Handles the request to retrieve info about the plugin"""
        #TODO - implement custom README viewer (see notes)
        busy_dlg = dialogs.progressDialog(dlg_title="Retrieving Plugin",
            dlg_msg="Please wait, downloading plugin...")
        try:
            self.fetch_plugin()
            readme = self.model.get_readme(self.get_configured_url())
            msg_dlg = wx.MessageDialog(self.view, message=readme, caption="README", style=wx.ICON_INFORMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
        except Exception as err:
            err_msg = "{0}".format(err)
            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                caption="Unable To Retrieve Plugin", style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()
        finally:
            busy_dlg.close()