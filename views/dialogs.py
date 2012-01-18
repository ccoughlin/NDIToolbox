"""dialogs.py - customized wxPython dialogs and convenience functions"""
import sys

__author__ = 'Chris R. Coughlin'

import views.ui_defaults as ui_defaults
import wx
from wx.lib.masked.numctrl import NumCtrl
from wx import ProgressDialog
import sys

class ImportTextDialog(wx.Dialog):
    """Specify import parameters for loading ASCII-delimited text files."""

    def __init__(self, parent, id=-1, title="Import Text File", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr):
        super(ImportTextDialog, self).__init__(parent, id, title, pos, size, style, name)
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
        self.delimchar_choice = wx.ComboBox(self, wx.ID_ANY, value=',', choices=self.delimiter_choices,
                                            style=wx.CB_DROPDOWN)
        self.delimchar_choice.SetToolTipString('Data in each row are separated with this character')
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
        self.cols_tc.SetToolTipString("Comma-delimited list of columns to read (first column is 0)")
        self.fsizer.Add(self.cols_tc, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                        ui_defaults.widget_margin)

        transpose_lbl = wx.StaticText(self, wx.ID_ANY, u'Transpose Array?',
                                      wx.DefaultPosition, wx.DefaultSize)
        self.fsizer.Add(transpose_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                        ui_defaults.widget_margin)
        self.transpose_cb = wx.CheckBox(self, wx.ID_ANY, u'Do not tranpose data', wx.DefaultPosition, wx.DefaultSize)
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
        params = {}
        params['delimiter'] = self._get_delim()
        params['commentchar'] = self.commentchar_tc.GetValue()
        params['skipheader'] = self.headerlines_ctrl.GetValue()
        params['skipfooter'] = self.footerlines_ctrl.GetValue()
        params['usecols'] = self._get_cols()
        params['transpose'] = self.transpose_cb.IsChecked()
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
        super(RangeDialog, self).__init__(parent=None, title=dlg_title)

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

    def GetValue(self):
        """Returns the tuple (start,finish) if the dialog was accepted."""
        return (self.start_ctrl.GetValue(), self.finish_ctrl.GetValue())


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

    def GetValue(self):
        """Returns the tuple (start,finish) if the dialog was accepted."""
        return (self.start_ctrl.GetValue(), self.finish_ctrl.GetValue())

class progressDialog(object):
    """Simple wrapper for wxPython's ProgressDialog,
    creates a pulsing progress bar to indicate busy status.
    Call close() when complete.  Recommended only when a
    very simple wait message is required.
    """
    def __init__(self,dlg_title,dlg_msg="Please wait..."):
        self.pdlg=ProgressDialog(message=dlg_msg,
            title=dlg_title,
            maximum=100#,
        )
        self.pdlg.Pulse()

    def close(self):
        self.pdlg.Update(100)
        self.pdlg.Destroy()