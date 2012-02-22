"""thumbnail_panel.py - shows thumbnail plot previews of selected data file

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import views.ui_defaults as ui_defaults
from controllers.thumbnailpanel_ctrl import ThumbnailPanelController
import wx

class ThumbnailPanel(wx.Panel):
    """Defines a simple thumbnail panel used to preview data plots"""

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TAB_TRAVERSAL | wx.NO_BORDER, name=wx.PanelNameStr):
        super(ThumbnailPanel, self).__init__(parent, id, pos, size, style, name)
        self.parent = parent
        self.controller = ThumbnailPanelController(self)
        self.bitmap_width = 300
        self.bitmap_height = 300
        self.init_ui()

    def init_ui(self):
        """Builds the wx Panel"""
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.figure_bmp = wx.StaticBitmap(self, wx.ID_ANY,
                                          bitmap=self.controller.empty_bitmap(self.bitmap_width,
                                                                              self.bitmap_height),
                                          pos=wx.DefaultPosition, size=wx.DefaultSize)
        self.panel_sizer.Add(self.figure_bmp, ui_defaults.ctrl_pct, wx.CENTER,
                             ui_defaults.widget_margin)
        self.SetSizerAndFit(self.panel_sizer)

    def plot_thumb(self, data_fname):
        """Generates a plot of the specified data file and sets the ThumbnailPanel's bitmap
        accordingly"""
        self.figure_bmp.SetBitmap(
            self.controller.plot_thumb(data_fname, self.bitmap_width, self.bitmap_height))

    def plot_blank(self):
        """Sets the ThumbnailPanel's bitmap to a placeholder bitmap when thumbnails are disabled"""
        self.figure_bmp.SetBitmap(self.controller.plot_blank())