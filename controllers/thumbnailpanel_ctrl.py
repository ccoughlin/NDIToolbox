"""thumbnail_ctrl.py - controller for the thumbnail_panel

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
from views.dialogs import ImportTextDialog
from models import thumbnailpanel_model as model
import wx
import os.path

class ThumbnailPanelController(object):
    """Controller class for the ThumbnailPanel"""

    def __init__(self, view):
        self.view = view

    def empty_bitmap(self, width, height):
        """Creates and returns an empty wxBitmap of the given width and height"""
        fg_color = wx.NullColor
        return wx.EmptyBitmapRGBA(width, height, fg_color.Red(), fg_color.Green(), fg_color.Blue())

    def plot_thumb(self, data_fname, width, height):
        """Creates (if necessary) and retrieves a matplotlib plot of the specified
        data file, returning a wx Bitmap"""
        thumbnail = self.empty_bitmap(width, height)
        if data_fname:
            thumb_fname = model.thumbnail_name(data_fname)
            if not os.path.exists(thumb_fname):
                # No thumbnail for this file exists, generate
                # TODO - redo data import if text files not used in final product
                import_dlg = ImportTextDialog(parent=self.view.parent)
                if import_dlg.ShowModal() == wx.ID_OK:
                    readtext_params = import_dlg.get_import_parameters()
                    thumbnail = model.multiprocess_plot(data_fname,
                                                        self.view.bitmap_width / 100,
                                                        self.view.bitmap_height / 100)

            else:
                # Thumbnail found, skip generation
                with open(thumb_fname, 'rb') as img_file:
                    img = wx.ImageFromStream(img_file, type=wx.BITMAP_TYPE_PNG)
                    thumbnail = wx.BitmapFromImage(img)
        return thumbnail

    def plot_blank(self):
        """Returns a wx Bitmap placeholder to display when thumbnails are disabled"""
        return wx.Bitmap(os.path.join(pathfinder.bitmap_path(), 'thumbs_disabled.png'))