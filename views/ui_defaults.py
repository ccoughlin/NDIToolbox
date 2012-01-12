"""ui_defaults.py - basic wxPython defaults to use across the application

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import wx

widget_margin = 3 # Default margin around widgets
ctrl_pct = 1.0 # Default to 100% resizing factor for controls
lbl_pct = 0.25 # Default to 25% resizing factor for labels
sizer_flags = wx.ALL | wx.EXPAND # Default resizing flags for controls
lblsizer_flags = wx.ALIGN_CENTRE_VERTICAL | wx.ALL # Default resizing flags for labels