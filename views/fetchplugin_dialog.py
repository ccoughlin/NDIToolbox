"""fetchplugin_idalog.py - dialog to configure remote fetch and inspection
of A7117 plugins

Chris R. Coughlin (TRI/Austin, Inc.)
"""
__author__ = 'Chris R. Coughlin'

from views import ui_defaults
from controllers import fetchplugin_dialog_ctrl
import wx

class FetchPluginDialog(wx.Dialog):
    """Dialog to configure local fetch and inspection
    of plugins"""

    def __init__(self, parent, plugin_path=None):
        super(FetchPluginDialog, self).__init__(parent=parent, title="Install Plugin")
        self.controller = fetchplugin_dialog_ctrl.FetchPluginDialogController(self)
        self.plugin_path = plugin_path
        self.init_ui()

    def init_ui(self):
        """Creates and lays out the UI"""
        self.main_panel_sizer = wx.FlexGridSizer(cols=2)

        loc_lbl = wx.StaticText(self, wx.ID_ANY, u"Plugin Location",
            wx.DefaultPosition, wx.DefaultSize)
        self.main_panel_sizer.Add(loc_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
            ui_defaults.widget_margin)
        self.url_tc = wx.TextCtrl(self, wx.ID_ANY, self.plugin_path,
            wx.DefaultPosition,
            wx.DefaultSize)
        self.url_tc.SetToolTipString("Full path and filename of plugin archive")
        self.main_panel_sizer.Add(self.url_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)

        # Set password on encrypted archives
        self.encryptedzip_cb = wx.CheckBox(self, wx.ID_ANY, u"Protected")
        self.encryptedzip_cb.SetToolTipString("Enable if the plugin archive is encrypted")
        self.main_panel_sizer.Add(self.encryptedzip_cb, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)

        zip_panel = wx.Panel(self)
        zip_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        zippword_lbl = wx.StaticText(zip_panel, wx.ID_ANY, u"Password",
            wx.DefaultPosition, wx.DefaultSize)
        zip_panel_sizer.Add(zippword_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
            ui_defaults.widget_margin)
        self.zippword_tc = wx.TextCtrl(zip_panel, wx.ID_ANY, u'', wx.DefaultPosition,
            wx.DefaultSize, style=wx.TE_PASSWORD)
        zip_panel_sizer.Add(self.zippword_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)
        zip_panel.SetSizerAndFit(zip_panel_sizer)
        self.main_panel_sizer.Add(zip_panel, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            0)
        self.about_plugin_btn = wx.Button(self, wx.ID_ANY, "About Plugin...", wx.DefaultPosition,
            wx.DefaultSize)
        self.about_plugin_btn.SetToolTipString("Displays the Plugin's README file")
        self.Bind(wx.EVT_BUTTON, self.controller.on_about_plugin, self.about_plugin_btn)
        self.main_panel_sizer.Add(self.about_plugin_btn, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            0)
        self._generate_std_buttons()
        self.SetSizerAndFit(self.main_panel_sizer)

    def _generate_std_buttons(self):
        """Generates the standard OK/Cancel dialog buttons"""
        self.stdbtns = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(self, wx.ID_OK)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        self.stdbtns.AddButton(ok_btn)
        self.stdbtns.AddButton(cancel_btn)
        self.stdbtns.Realize()
        self.main_panel_sizer.Add(self.stdbtns, ui_defaults.lbl_pct, ui_defaults.sizer_flags,
            0)

    def install_plugin(self):
        """Attempts to download, verify, and install the plugin archive"""
        self.controller.install_plugin()


class FetchRemotePluginDialog(wx.Dialog):
    """Dialog to configure remote fetch and inspection
    of A7117 Plugins"""

    def __init__(self, parent):
        super(FetchRemotePluginDialog, self).__init__(parent=parent, title="Install Plugin")
        self.controller = fetchplugin_dialog_ctrl.FetchRemotePluginDialogController(self)
        self.init_ui()

    def install_plugin(self):
        """Attempts to download, verify, and install the plugin archive"""
        self.controller.install_plugin()

    def init_ui(self):
        """Creates and lays out the UI"""
        self.main_panel_sizer = wx.FlexGridSizer(cols=2)

        url_lbl = wx.StaticText(self, wx.ID_ANY, u"Plugin URL",
            wx.DefaultPosition, wx.DefaultSize)
        self.main_panel_sizer.Add(url_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
            ui_defaults.widget_margin)
        self.url_tc = wx.TextCtrl(self, wx.ID_ANY, u'http://',
            wx.DefaultPosition,
            wx.DefaultSize)
        self.url_tc.SetToolTipString("Example: http://www.tri-austin.com/a7117/my_plugin.zip")
        self.main_panel_sizer.Add(self.url_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)

        # Set username/password if necessary
        self.login_cb = wx.CheckBox(self, wx.ID_ANY, u"Login Required")
        self.login_cb.SetToolTipString("Enable if the URL requires a username and password")
        self.main_panel_sizer.Add(self.login_cb, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)
        login_panel = wx.Panel(self)
        login_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        uname_lbl = wx.StaticText(login_panel, wx.ID_ANY, u"Username",
            wx.DefaultPosition, wx.DefaultSize)
        login_panel_sizer.Add(uname_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
            ui_defaults.widget_margin)
        self.uname_tc = wx.TextCtrl(login_panel, wx.ID_ANY, u'', wx.DefaultPosition,
            wx.DefaultSize)
        login_panel_sizer.Add(self.uname_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)
        pword_lbl = wx.StaticText(login_panel, wx.ID_ANY, u"Password",
            wx.DefaultPosition, wx.DefaultSize)
        login_panel_sizer.Add(pword_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
            ui_defaults.widget_margin)
        self.pword_tc = wx.TextCtrl(login_panel, wx.ID_ANY, u'', wx.DefaultPosition,
            wx.DefaultSize, style=wx.TE_PASSWORD)
        login_panel_sizer.Add(self.pword_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)
        login_panel.SetSizerAndFit(login_panel_sizer)
        self.main_panel_sizer.Add(login_panel, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            0)

        # Set password on encrypted archives
        self.encryptedzip_cb = wx.CheckBox(self, wx.ID_ANY, u"Protected")
        self.encryptedzip_cb.SetToolTipString("Enable if the plugin archive is encrypted")
        self.main_panel_sizer.Add(self.encryptedzip_cb, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)

        zip_panel = wx.Panel(self)
        zip_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        zippword_lbl = wx.StaticText(zip_panel, wx.ID_ANY, u"Password",
            wx.DefaultPosition, wx.DefaultSize)
        zip_panel_sizer.Add(zippword_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
            ui_defaults.widget_margin)
        self.zippword_tc = wx.TextCtrl(zip_panel, wx.ID_ANY, u'', wx.DefaultPosition,
            wx.DefaultSize, style=wx.TE_PASSWORD)
        zip_panel_sizer.Add(self.zippword_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)
        zip_panel.SetSizerAndFit(zip_panel_sizer)
        self.main_panel_sizer.Add(zip_panel, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            0)
        self.about_plugin_btn = wx.Button(self, wx.ID_ANY, "About Plugin...", wx.DefaultPosition,
            wx.DefaultSize)
        self.about_plugin_btn.SetToolTipString("Displays the Plugin's README file")
        self.Bind(wx.EVT_BUTTON, self.controller.on_about_plugin, self.about_plugin_btn)
        self.main_panel_sizer.Add(self.about_plugin_btn, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            0)
        self._generate_std_buttons()
        self.SetSizerAndFit(self.main_panel_sizer)

    def _generate_std_buttons(self):
        """Generates the standard OK/Cancel dialog buttons"""
        self.stdbtns = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(self, wx.ID_OK)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        self.stdbtns.AddButton(ok_btn)
        self.stdbtns.AddButton(cancel_btn)
        self.stdbtns.Realize()
        self.main_panel_sizer.Add(self.stdbtns, ui_defaults.lbl_pct, ui_defaults.sizer_flags,
            0)