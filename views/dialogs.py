"""dialogs.py - customized wxPython dialogs and convenience functions"""

__author__ = 'Chris R. Coughlin'

import views.ui_defaults as ui_defaults
from controllers import pathfinder
from models.mainmodel import get_logger
import wx
from wx.lib.masked.numctrl import NumCtrl
from wx.lib import statbmp, wordwrap
from wx import ProgressDialog
import os
import sys
import textwrap
import webbrowser

module_logger = get_logger(__name__)

class ImportTextDialog(wx.Dialog):
    """Specify import parameters for loading ASCII-delimited text files."""

    def __init__(self, parent, id=-1, title="Import Text File", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr):
        super(ImportTextDialog, self).__init__(parent, id, title, pos, size, style, name)
        module_logger.info("Succesfully initialized ImportTextDialog.")
        self.generate()

    def generate(self):
        """Creates the UI"""
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.fsizer = wx.FlexGridSizer(cols=2)

        commentchar_lbl = wx.StaticText(self, wx.ID_ANY, u'Comment Character:',
                                        wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(commentchar_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.commentchar_tc = wx.TextCtrl(self, wx.ID_ANY, u'#', wx.DefaultPosition,
                                          wx.DefaultSize)
        self.commentchar_tc.SetToolTipString('Lines beginning with this character are ignored')
        self.fsizer.Add(self.commentchar_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)

        delimchar_lbl = wx.StaticText(self, wx.ID_ANY, u'Delimiter Character:',
                                      wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(delimchar_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.delimiter_choices = [',', 'Whitespace (TAB, Space, etc.)', ':', ';', '|', '/']
        self.delimchar_choice = wx.ComboBox(self, wx.ID_ANY, value=',',
                                            choices=self.delimiter_choices,
                                            style=wx.CB_DROPDOWN)
        self.delimchar_choice.SetToolTipString('Data in each row are separated with this '
                                               'character')
        self.fsizer.Add(self.delimchar_choice, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)

        skipheader_lbl = wx.StaticText(self, wx.ID_ANY, u'Lines In Header:',
                                       wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(skipheader_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.headerlines_ctrl = wx.SpinCtrl(self, wx.ID_ANY, '0')
        self.headerlines_ctrl.SetToolTipString("Number of lines to skip at beginning of file")
        self.headerlines_ctrl.SetRange(0, 1e6)
        self.fsizer.Add(self.headerlines_ctrl, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)

        skipfooter_lbl = wx.StaticText(self, wx.ID_ANY, u'Lines In Footer:',
                                       wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(skipfooter_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.footerlines_ctrl = wx.SpinCtrl(self, wx.ID_ANY, '0')
        self.footerlines_ctrl.SetToolTipString("Number of lines to skip at end of file")
        self.footerlines_ctrl.SetRange(0, 1e6)
        self.fsizer.Add(self.footerlines_ctrl, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)

        cols_lbl = wx.StaticText(self, wx.ID_ANY, u'Columns To Read:',
                                 wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(cols_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.cols_tc = wx.TextCtrl(self, wx.ID_ANY, u'All', wx.DefaultPosition, wx.DefaultSize)
        self.cols_tc.SetToolTipString("Comma-delimited list of columns to read (first column is "
                                      "0)")
        self.fsizer.Add(self.cols_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)

        transpose_lbl = wx.StaticText(self, wx.ID_ANY, u'Transpose Array?',
                                      wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(transpose_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.transpose_cb = wx.CheckBox(self, wx.ID_ANY, u'Do not tranpose data',
                                        wx.DefaultPosition
                                        , wx.DefaultSize)
        self.transpose_cb.SetToolTipString("Check this box to transpose the data array after load")
        self.Bind(wx.EVT_CHECKBOX, self.on_transpose_cb, self.transpose_cb)
        self.fsizer.Add(self.transpose_cb, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)

        self.sizer.Add(self.fsizer, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)
        self._generate_std_buttons()
        self.SetSizerAndFit(self.sizer)

    def _generate_std_buttons(self):
        """Generates the standard OK/Cancel dialog buttons"""
        self.stdbtns = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(self, wx.ID_OK)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        self.stdbtns.AddButton(ok_btn)
        self.stdbtns.AddButton(cancel_btn)
        self.stdbtns.Realize()
        self.sizer.Add(self.stdbtns, ui_defaults.lbl_pct, ui_defaults.sizer_flags,
                       ui_defaults.widget_margin)

    def on_transpose_cb(self, evt):
        """Updates the Tranpose checkbox label with the current setting"""
        if self.transpose_cb.IsChecked():
            self.transpose_cb.SetLabel('Tranpose data')
        else:
            self.transpose_cb.SetLabel('Do not tranpose data')

    def _get_cols(self):
        """Returns tuple of columns to read, or None if all are to be read"""
        raw_str = self.cols_tc.GetValue()
        if raw_str:
            try:
                cols = [int(col) for col in raw_str.split(',')]
                if len(cols) > 0:
                    return cols
                return None
            except ValueError:
                return None

    def _get_delim(self):
        """Returns the specified delimiter character"""
        raw_delim = self.delimchar_choice.GetValue()
        if "whitespace" in raw_delim.lower():
            return None
        return raw_delim[0]

    def get_import_parameters(self):
        """Returns a dict of the text import parameters"""
        #params = {}
        params = {'delimiter':self._get_delim(),
                  'commentchar':self.commentchar_tc.GetValue(),
                  'skipheader':self.headerlines_ctrl.GetValue(),
                  'skipfooter':self.footerlines_ctrl.GetValue(),
                  'usecols':self._get_cols(),
                  'transpose':self.transpose_cb.IsChecked()}
        return params


class ExportTextDialog(wx.Dialog):
    """Specify export parameters for saving data to delimited ASCII"""

    def __init__(self, parent, id=-1, title="Export Text File", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr):
        super(ExportTextDialog, self).__init__(parent, id, title, pos, size, style, name)
        self.delimiter_choices = {"Comma": ",",
                                  "Space": " ",
                                  "TAB": "\t"}
        self.format_choices = {"Float (e.g. 1.00)": "%f",
                               "Integer (e.g. 1)": "%i",
                               "Scientific Notation (e.g. 1.00E2)": "%e"}
        self.eol_choices = {"Linefeed (\\n)": "\n",
                            "Carriage Return + Linefeed (\\r\\n)": "\r\n"}
        module_logger.info("Successfully initialized ExportTextDialog.")
        self.generate()

    def generate(self):
        """Creates the UI"""
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.fsizer = wx.FlexGridSizer(cols=2)

        delim_lbl = wx.StaticText(self, wx.ID_ANY, u'Delimiter Character:',
                                  wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(delim_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.delim_combobox = wx.ComboBox(self, wx.ID_ANY, self.delimiter_choices.keys()[0],
                                          wx.DefaultPosition, wx.DefaultSize,
                                          self.delimiter_choices.keys())
        self.delim_combobox.SetSelection(0)
        self.fsizer.Add(self.delim_combobox, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)
        fmt_lbl = wx.StaticText(self, wx.ID_ANY, u'Format',
                                wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(fmt_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.fmt_combobox = wx.ComboBox(self, wx.ID_ANY, self.format_choices.keys()[0],
                                        wx.DefaultPosition, wx.DefaultSize,
                                        self.format_choices.keys())
        self.fmt_combobox.SetSelection(0)
        self.fsizer.Add(self.fmt_combobox, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)
        nline_lbl = wx.StaticText(self, wx.ID_ANY, u'End Of Line Character', wx.DefaultPosition,
                                  wx.DefaultSize)
        self.fsizer.Add(nline_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.nline_combobox = wx.ComboBox(self, wx.ID_ANY, self.eol_choices.keys()[0],
                                          wx.DefaultPosition, wx.DefaultSize,
                                          self.eol_choices.keys())
        self.nline_combobox.SetSelection(0)
        self.fsizer.Add(self.nline_combobox, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)
        self.sizer.Add(self.fsizer, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)
        self._generate_std_buttons()
        self.SetSizerAndFit(self.sizer)

    def _generate_std_buttons(self):
        """Generates the standard OK/Cancel dialog buttons"""
        self.stdbtns = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(self, wx.ID_OK)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        self.stdbtns.AddButton(ok_btn)
        self.stdbtns.AddButton(cancel_btn)
        self.stdbtns.Realize()
        self.sizer.Add(self.stdbtns, ui_defaults.lbl_pct, ui_defaults.sizer_flags,
                       ui_defaults.widget_margin)

    def get_export_parameters(self):
        """Returns a dict of the text export parameters"""
        params = {'delimiter':self.delimiter_choices.get(self.delim_combobox.GetStringSelection(), ","),
                  'format':self.format_choices.get(self.fmt_combobox.GetStringSelection(), "%f"),
                  'newline':self.eol_choices.get(self.nline_combobox.GetStringSelection(), "\n")}
        return params


class IntegerRangeDialog(wx.Dialog):
    """Dialog to specify a numeric range.  Defaults to allowing
    any integer between 0 and the maximum for an integer for the
    platform (sys.maxint) for both the start and finish values of
    the range.  Returns a tuple (start,finish) if accepted (i.e.
    the rangeDialog instance's .ShowModal() returns wx.ID_OK).
    """

    def __init__(self, dlg_title, dlg_msg='Please enter a range.',
                 start_range_lbl='Min', finish_range_lbl='Max',
                 start_min=0, start_max=sys.maxint,
                 finish_min=0, finish_max=sys.maxint):
        super(IntegerRangeDialog, self).__init__(parent=None, title=dlg_title)

        vbox = wx.BoxSizer(wx.VERTICAL)
        msg_text = wx.StaticText(self, -1, dlg_msg)
        vbox.Add(msg_text, 0, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.start_ctrl = wx.SpinCtrl(self, -1, min=start_min, max=start_max)
        hbox1.Add(wx.StaticText(self, -1, start_range_lbl), 1, ui_defaults.lblsizer_flags,
                  ui_defaults.widget_margin)
        hbox1.Add(self.start_ctrl, 0, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.finish_ctrl = wx.SpinCtrl(self, -1, min=finish_min, max=finish_max)
        hbox2.Add(wx.StaticText(self, -1, finish_range_lbl), 1, ui_defaults.lblsizer_flags,
                  ui_defaults.widget_margin)
        hbox2.Add(self.finish_ctrl, 0, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        hbox3.Add(btns, 1, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        vbox.Add(hbox1, 0, ui_defaults.sizer_flags, 0)
        vbox.Add(hbox2, 0, ui_defaults.sizer_flags, 0)
        vbox.Add(hbox3, 0, wx.ALIGN_RIGHT, 0)
        self.SetSizer(vbox)
        self.SetInitialSize()
        module_logger.info("Successfully initialized IntegerRangeDialog.")

    def GetValue(self):
        """Returns the tuple (start,finish) if the dialog was accepted."""
        return self.start_ctrl.GetValue(), self.finish_ctrl.GetValue()


class FloatRangeDialog(wx.Dialog):
    """Dialog to specify a floating-point numeric range.  Defaults to allowing any
    floating-point value (system-dependent) for both start and finish values.  Returns
    a tuple (start, finish) if accepted."""

    def __init__(self, dlg_title, dlg_msg='Please enter a range.',
                 start_range_lbl='Min', finish_range_lbl='Max',
                 start_min=None, start_max=None,
                 finish_min=None, finish_max=None):
        super(FloatRangeDialog, self).__init__(parent=None, title=dlg_title)
        vbox = wx.BoxSizer(wx.VERTICAL)
        msg_text = wx.StaticText(self, wx.ID_ANY, dlg_msg)
        vbox.Add(msg_text, 0, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.start_ctrl = NumCtrl(self, wx.ID_ANY, pos=wx.DefaultPosition,
                                  size=wx.DefaultSize)
        if start_min is not None:
            self.start_ctrl.SetMin(start_min)
        if start_max is not None:
            self.start_ctrl.SetMax(start_max)
        hbox1.Add(wx.StaticText(self, -1, start_range_lbl), 1, ui_defaults.lblsizer_flags,
                  ui_defaults.widget_margin)
        hbox1.Add(self.start_ctrl, 0, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.finish_ctrl = NumCtrl(self, wx.ID_ANY, pos=wx.DefaultPosition,
                                   size=wx.DefaultSize)
        if finish_min is not None:
            self.finish_ctrl.SetMin(finish_min)
        if finish_max is not None:
            self.finish_ctrl.SetMax(finish_max)
        hbox2.Add(wx.StaticText(self, -1, finish_range_lbl), 1, ui_defaults.lblsizer_flags,
                  ui_defaults.widget_margin)
        hbox2.Add(self.finish_ctrl, 0, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        hbox3.Add(btns, 1, ui_defaults.sizer_flags, ui_defaults.widget_margin)
        vbox.Add(hbox1, 0, ui_defaults.sizer_flags, 0)
        vbox.Add(hbox2, 0, ui_defaults.sizer_flags, 0)
        vbox.Add(hbox3, 0, wx.ALIGN_RIGHT, 0)
        self.SetSizer(vbox)
        self.SetInitialSize()
        module_logger.info("Successfully initialized FloatRangeDialog.")

    def GetValue(self):
        """Returns the tuple (start,finish) if the dialog was accepted."""
        return self.start_ctrl.GetValue(), self.finish_ctrl.GetValue()


class progressDialog(object):
    """Simple wrapper for wxPython's ProgressDialog,
    creates a pulsing progress bar to indicate busy status.
    Call close() when complete.  Recommended only when a
    very simple wait message is required.
    """

    def __init__(self, dlg_title, dlg_msg="Please wait..."):
        self.pdlg = ProgressDialog(message=dlg_msg,
                                   title=dlg_title,
                                   maximum=100#,
        )
        self.pdlg.Pulse()
        module_logger.info("Successfully initialized progressDialog.")

    def update(self):
        self.pdlg.UpdatePulse()

    def close(self):
        self.pdlg.Update(100)
        module_logger.info("Closing progressDialog.")
        self.pdlg.Destroy()


class AboutDialog(wx.Dialog):
    """Simple About dialog that displays a bitmap logo and provides
    an option to go to a specified website."""

    def __init__(self, parent, id=-1, title='About This Program', pos=None,
                 size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr,
                 msg=None, logobmp_fname=None, url=None):
        self.parent = parent
        super(AboutDialog, self).__init__(parent, id, title, pos, size, style, name)
        self.msg = msg
        self.logo_fn = logobmp_fname
        self.url = url
        self.generate()

    def generate(self):
        """Creates the UI"""
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        logo = self.get_bmp()
        if logo is not None:
            self.bitmap_logo = statbmp.GenStaticBitmap(self, wx.ID_ANY, logo,
                                                       style=wx.ALIGN_CENTRE,
                                                       size=(logo.GetWidth(), logo.GetHeight()))
            if self.url is not None:
                self.bitmap_logo.SetToolTipString("Visit {0}".format(self.url))
                self.bitmap_logo.Bind(wx.EVT_LEFT_DOWN, self.on_click, self.bitmap_logo)
            self.sizer.Add(self.bitmap_logo, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                           ui_defaults.widget_margin)
        if self.msg is not None:
            dc = wx.ClientDC(self)
            if logo is not None:
                wrap_width = logo.GetWidth()
                if sys.platform == 'win32':
                    wrap_width *= 1.3
            else:
                wrap_width = self.GetClientSizeTuple()[0]
            self.msg = wordwrap.wordwrap(textwrap.dedent(self.msg), wrap_width, dc)
            self.msg_lbl = wx.StaticText(self, wx.ID_ANY, self.msg,
                                         pos=wx.DefaultPosition,
                                         size=wx.DefaultSize)
            self.sizer.Add(self.msg_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                           ui_defaults.widget_margin)
        self.SetSizerAndFit(self.sizer)
        self.Centre()

    def get_bmp(self):
        """Loads the specified bitmap into the UI"""
        if os.path.exists(self.logo_fn):
            return wx.Bitmap(name=self.logo_fn, type=wx.BITMAP_TYPE_PNG)
        return None

    def on_click(self, evt):
        """Handles the click event in the About Dialog by
        loading the specified URL in the user's default
        web browser."""
        if self.url is not None:
            webbrowser.open(self.url)


class ConfigurePluginDialog(wx.Dialog):
    """wxPython dialog to allow user configuration of NDIToolbox
    plugins"""

    def __init__(self, parent, plugin_instance):
        self.parent = parent
        self.plugin = plugin_instance
        title = "Configure Plugin"
        super(ConfigurePluginDialog, self).__init__(parent, wx.ID_ANY, title,
                                                    wx.DefaultPosition, wx.DefaultSize,
                                                    wx.DEFAULT_DIALOG_STYLE)
        module_logger.info("Successfully initialized ConfigurePluginDialog.")
        self.generate()

    def generate(self):
        """Lays out and builds the dialog"""
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        desc_panel = wx.Panel(self)
        desc_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        plugin_lbl = wx.StaticText(desc_panel, wx.ID_ANY, self.plugin.name)
        plugin_lbl_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        plugin_lbl.SetFont(plugin_lbl_font)
        desc_panel_sizer.Add(plugin_lbl, ui_defaults.lbl_pct,
                             ui_defaults.lblsizer_flags, ui_defaults.widget_margin)
        description_lbl = wx.StaticText(desc_panel, wx.ID_ANY, self.plugin.description)
        desc_panel_sizer.Add(description_lbl, ui_defaults.lbl_pct,
                             ui_defaults.lblsizer_flags, ui_defaults.widget_margin)
        desc_panel.SetSizer(desc_panel_sizer)
        self.sizer.Add(desc_panel, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags, 0)
        self.config_panel = wx.ScrolledWindow(self, wx.ID_ANY)
        self.config_panel_sizer = wx.FlexGridSizer(cols=2)
        self.config_panel_sizer.AddGrowableCol(1)
        self.config_ctrls = self.populate_config()
        for lbl, ctrl in self.config_ctrls.items():
            opt_lbl = wx.StaticText(self.config_panel, wx.ID_ANY, lbl)
            self.config_panel_sizer.Add(opt_lbl, ui_defaults.lbl_pct,
                                        ui_defaults.lblsizer_flags,
                                        ui_defaults.widget_margin)
            self.config_panel_sizer.Add(ctrl, ui_defaults.ctrl_pct,
                                        ui_defaults.sizer_flags,
                                        ui_defaults.widget_margin)
        self.config_panel.SetSizerAndFit(self.config_panel_sizer)
        self.sizer.Add(self.config_panel, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)
        self._generate_std_buttons()
        self.SetSizerAndFit(self.sizer)
        self.CentreOnScreen()

    def _generate_std_buttons(self):
        """Generates the standard OK/Cancel dialog buttons"""
        self.stdbtns = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(self, wx.ID_OK)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        self.stdbtns.AddButton(ok_btn)
        self.stdbtns.AddButton(cancel_btn)
        self.stdbtns.Realize()
        self.sizer.Add(self.stdbtns, ui_defaults.lbl_pct, ui_defaults.sizer_flags, ui_defaults.widget_margin)

    def populate_config(self):
        config_ctrls = {}
        for opt, setting in self.plugin.config.items():
            opt_ctrl = wx.TextCtrl(self.config_panel, wx.ID_ANY, value=str(setting))
            config_ctrls[opt] = opt_ctrl
        return config_ctrls

    def get_config(self):
        config = {}
        for opt, ctrl in self.config_ctrls.items():
            config[opt] = ctrl.GetValue()
        return config


class TextDisplayDialog(wx.Dialog):
    """Simple wxPython window to display large blocks of text"""

    def __init__(self, text, parent=None, wrap=True, *args, **kwargs):
        self.parent = parent
        self.text = text
        self.wrap_text = wrap
        wx.Dialog.__init__(self, parent, *args, **kwargs)
        if self.parent is not None:
            self.SetIcon(self.parent.GetIcon())
        self.init_ui()

    def init_ui(self):
        """Initializes and lays out the UI"""
        self.SetClientSize(wx.Size(400, 300))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.textfilew_tc = wx.TextCtrl(self.main_panel, wx.ID_ANY, ''.join(self.text),
                                        wx.DefaultPosition, wx.DefaultSize, style=wx.TE_MULTILINE)
        self.main_panel_sizer.Add(self.textfilew_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.textfile_tc = wx.TextCtrl(self.main_panel, wx.ID_ANY, ''.join(self.text),
                                       wx.DefaultPosition, wx.DefaultSize,
                                       style=wx.TE_MULTILINE | wx.TE_DONTWRAP)
        self.main_panel_sizer.Add(self.textfile_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.set_text_wrap(self.wrap_text)
        ctrl_panel = wx.Panel(self.main_panel)
        ctrl_sizer = wx.FlexGridSizer(cols=2)
        ctrl_sizer.SetFlexibleDirection(wx.HORIZONTAL)
        ctrl_sizer.AddGrowableCol(0)
        wrap_cb = wx.CheckBox(ctrl_panel, wx.ID_ANY, u"Wrap Text")
        wrap_cb.SetValue(self.wrap_text)
        ctrl_sizer.Add(wrap_cb, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)
        self.Bind(wx.EVT_CHECKBOX, self.on_toggle_wrap, wrap_cb)
        ok_btn = wx.Button(ctrl_panel, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.on_ok_btn, ok_btn)
        ok_btn.SetFocus()
        ctrl_sizer.Add(ok_btn, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)
        ctrl_panel.SetSizerAndFit(ctrl_sizer)
        self.main_panel_sizer.Add(ctrl_panel, ui_defaults.lbl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.main_panel.SetSizer(self.main_panel_sizer)
        self.sizer.Add(self.main_panel, 1, ui_defaults.sizer_flags, 0)
        self.SetSizer(self.sizer)

    def on_toggle_wrap(self, evt):
        """Handles request to enable/disable text wrapping in display"""
        self.set_text_wrap(evt.IsChecked())

    def set_text_wrap(self, wrap):
        """Toggles between the two TextCtrls to enable (wrap=True)
        or disable (wrap=False) text wrapping in the window.  Used
        to circumvent limitations in Windows re: changing control styles
        dynamically."""
        if wrap:
            self.textfilew_tc.SetSize(self.textfile_tc.GetSize())
            self.textfile_tc.Hide()
            self.main_panel_sizer.Show(self.textfilew_tc)
        else:
            self.textfile_tc.SetSize(self.textfilew_tc.GetSize())
            self.textfilew_tc.Hide()
            self.main_panel_sizer.Show(self.textfile_tc)
        self.main_panel_sizer.Layout()

    def on_ok_btn(self, evt):
        """Handles request to close the window"""
        self.Destroy()


class LinearSliceDialog(wx.Dialog):
    """Dialog to select a linear slice in one of the axes of an array"""

    def __init__(self, data, parent=None, *args, **kwargs):
        self.parent = parent
        self.data = data
        super(LinearSliceDialog, self).__init__(parent, *args, **kwargs)
        if self.parent is not None:
            self.SetIcon(self.parent.GetIcon())
        self.init_ui()
        module_logger.info("Successfully initialized LinearSliceDialog.")

    def init_ui(self):
        """Initializes and lays out the UI"""
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        description_lbl = wx.StaticText(self.main_panel, wx.ID_ANY, "Please specify axis indices.")
        self.main_panel_sizer.Add(description_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                                  ui_defaults.widget_margin)
        self._generate_axis_ctrls()

        self.main_panel.SetSizer(self.main_panel_sizer)
        self.sizer.Add(self.main_panel, 1, ui_defaults.sizer_flags, 0)
        self._generate_std_buttons()
        self.SetSizerAndFit(self.sizer)

    def _generate_axis_ctrls(self):
        """Creates and adds the SpinCtrls for each axis to the dialog"""

        def generate_axis_sc(axis_idx):
            """Helper function to return a SpinCtrl with minimum and maximum
            values set according to the dimensions of the data's axis"""
            return wx.SpinCtrl(self.main_panel, wx.ID_ANY, min=-1, max=self.data.shape[axis_idx] - 1)

        self.axes = {"X Axis": generate_axis_sc(0),
                     "Y Axis": generate_axis_sc(1),
                     "Z Axis": generate_axis_sc(2)}
        for axis_name, axis_sc in sorted(self.axes.items()):
            axis_sizer = wx.BoxSizer(wx.HORIZONTAL)
            axis_lbl = wx.StaticText(self.main_panel, wx.ID_ANY, axis_name)
            axis_sizer.Add(axis_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                           ui_defaults.widget_margin)
            axis_sizer.Add(axis_sc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                           ui_defaults.widget_margin)
            self.main_panel_sizer.Add(axis_sizer, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)

    def _generate_std_buttons(self):
        """Generates the standard OK/Cancel dialog buttons"""
        self.stdbtns = wx.StdDialogButtonSizer()
        help_btn = wx.Button(self, wx.ID_HELP)
        self.Bind(wx.EVT_BUTTON, self.on_help, help_btn)
        ok_btn = wx.Button(self, wx.ID_OK)
        ok_btn.SetFocus()
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        self.stdbtns.AddButton(help_btn)
        self.stdbtns.AddButton(ok_btn)
        self.stdbtns.AddButton(cancel_btn)
        self.stdbtns.Realize()
        self.sizer.Add(self.stdbtns, ui_defaults.lbl_pct, ui_defaults.sizer_flags, ui_defaults.widget_margin)

    def get_data_slice(self):
        """Returns a slice of the dialog's 3D NumPy array."""
        x_idx = self.axes["X Axis"].GetValue()
        y_idx = self.axes["Y Axis"].GetValue()
        z_idx = self.axes["Z Axis"].GetValue()
        module_logger.info("Requested slice with indices {0}, {1}, {2}.".format(x_idx, y_idx, z_idx))
        if x_idx == -1:
            x_idx = slice(None)
        if y_idx == -1:
            y_idx = slice(None)
        if z_idx == -1:
            z_idx = slice(None)
        return self.data[y_idx, x_idx, z_idx]

    def on_help(self, evt):
        """Responds to request for help with the dialog
        by displaying basic how-to info"""
        with open(os.path.join(pathfinder.textfiles_path(), "slice3d_dlg.txt"), "rb") as fidin:
            help_dlg = TextDisplayDialog(text=fidin.readlines(), parent=self, title="Slicing 3D Data",
                                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
            help_dlg.ShowModal()
            help_dlg.Destroy()


class PlanarSliceDialog(wx.Dialog):
    """Dialog to select a plane in X, Y, or Z in 3D data"""

    def __init__(self, data, parent=None, *args, **kwargs):
        self.parent = parent
        self.data = data
        super(PlanarSliceDialog, self).__init__(parent, *args, **kwargs)
        if self.parent is not None:
            self.SetIcon(self.parent.GetIcon())
        self.init_ui()
        module_logger.info("Successfully initialized PlanarSliceDialog.")

    @property
    def planes(self):
        """Returns list of available planes"""
        return ["Parallel To X-Y (Index In Z)", "Parallel To X-Z (Index In Y)", "Parallel To Y-Z (Index In X)"]

    def init_ui(self):
        """Initializes and lays out the UI"""
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        glyph_fn = os.path.join(pathfinder.bitmap_path(), "axis_glyph_sm.png")
        glyph = wx.Bitmap(glyph_fn, type=wx.BITMAP_TYPE_PNG)
        glyph_ctrl = statbmp.GenStaticBitmap(self.main_panel, wx.ID_ANY, glyph, style=wx.ALIGN_CENTRE_VERTICAL,
                                             size=(glyph.GetWidth(), glyph.GetHeight()))
        self.main_panel_sizer.Add(glyph_ctrl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                                  ui_defaults.widget_margin)
        ctrl_panel = wx.Panel(self.main_panel)
        ctrl_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        instructions_txt = '\n'.join(['To continue, please specify a plane in the 3-D data.',
                                      'A plane is defined by an orientation and an index',
                                      'into the data. Orientation determines which direction',
                                      'the slice is made, and the index specifies where in',
                                      'the remaining axis the slice is made.'])
        instructions_lbl = wx.StaticText(ctrl_panel, wx.ID_ANY, instructions_txt)
        ctrl_panel_sizer.Add(instructions_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                             ui_defaults.widget_margin)

        orientation_panel = wx.Panel(ctrl_panel)
        orientation_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        orientation_lbl = wx.StaticText(orientation_panel, wx.ID_ANY, "Orientation")
        orientation_panel_sizer.Add(orientation_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                                    ui_defaults.widget_margin)

        self.plane_choice = wx.Choice(orientation_panel, wx.ID_ANY, choices=self.planes)

        orientation_panel_sizer.Add(self.plane_choice, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                                    ui_defaults.widget_margin)
        orientation_panel.SetSizerAndFit(orientation_panel_sizer)
        ctrl_panel_sizer.Add(orientation_panel, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)

        idx_panel = wx.Panel(ctrl_panel)
        idx_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        idx_lbl = wx.StaticText(idx_panel, wx.ID_ANY, "Index")
        idx_panel_sizer.Add(idx_lbl, ui_defaults.ctrl_pct, ui_defaults.lblsizer_flags, ui_defaults.widget_margin)
        self.idx_sc = wx.SpinCtrl(idx_panel, wx.ID_ANY)
        idx_panel_sizer.Add(self.idx_sc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                            ui_defaults.widget_margin)
        idx_panel.SetSizerAndFit(idx_panel_sizer)
        self.Bind(wx.EVT_CHOICE, self.on_orientation_change, self.plane_choice)
        self.plane_choice.SetSelection(0)
        self.set_index_limits()
        ctrl_panel_sizer.Add(idx_panel, ui_defaults.ctrl_pct, ui_defaults.sizer_flags, 0)
        ctrl_panel.SetSizerAndFit(ctrl_panel_sizer)
        self.main_panel_sizer.Add(ctrl_panel, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags, 0)
        self.main_panel.SetSizer(self.main_panel_sizer)
        self.sizer.Add(self.main_panel, 1, ui_defaults.sizer_flags, 0)
        self._generate_std_buttons()
        self.SetSizerAndFit(self.sizer)

    def _generate_std_buttons(self):
        """Generates the standard OK/Cancel dialog buttons"""
        self.stdbtns = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(self, wx.ID_OK)
        ok_btn.SetFocus()
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        self.stdbtns.AddButton(ok_btn)
        self.stdbtns.AddButton(cancel_btn)
        self.stdbtns.Realize()
        self.sizer.Add(self.stdbtns, ui_defaults.lbl_pct, ui_defaults.sizer_flags, ui_defaults.widget_margin)

    def on_orientation_change(self, evt):
        """Handles change in orientation choice"""
        self.set_index_limits()

    def set_index_limits(self):
        """Sets appropriate maximum for index based on selected orientation"""
        if self.data is not None:
            data_shape = self.data.shape
            selected_plane_idx = self.plane_choice.GetSelection()
            max_idx = sys.float_info.max
            if selected_plane_idx == 0: # Z index
                max_idx = data_shape[2] - 1
            elif selected_plane_idx == 1: # Y index
                max_idx = data_shape[0] - 1
            elif selected_plane_idx == 2: # X index
                max_idx = data_shape[1] - 1
            self.idx_sc.SetRange(0, max_idx)

    def get_data_slice(self):
        """Returns a planar slice of the 3D data from the current
        orientation and index choices"""
        idx = self.idx_sc.GetValue()
        selected_plane_idx = self.plane_choice.GetSelection()
        module_logger.info("Requested slice with index {0} in plane index {1}.".format(idx, selected_plane_idx))
        if selected_plane_idx == 0: # Z index
            return self.data[:, :, idx]
        elif selected_plane_idx == 1: # Y index
            return self.data[idx, :, :]
        elif selected_plane_idx == 2: # X index
            return self.data[:, idx, :]