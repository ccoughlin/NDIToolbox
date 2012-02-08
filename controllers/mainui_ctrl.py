""" mainui_ctrl.py - controller for mainui

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import mainmodel
import views.plotwindow as plotwindow
import views.preview_window as preview_window
import views.dialogs as dlg
import controllers.pathfinder as pathfinder
import wx
import os.path

class MainUIController(object):
    """Controller for the main user interface"""

    def __init__(self, view):
        self.view = view
        self.init_model()

    def init_model(self):
        """Creates and connects the model"""
        self.model = mainmodel.MainModel(self)

    def get_icon_bmp(self):
        """Returns a PNG wx.Bitmap of the application's
        default icon"""
        icon_bmp_path = pathfinder.icon_path()
        return wx.Bitmap(icon_bmp_path, wx.BITMAP_TYPE_PNG)

    def get_icon(self):
        """Returns a wx.Icon of the application's
        default icon"""
        return wx.IconFromBitmap(self.get_icon_bmp())

    def get_bitmap(self, bitmap_name):
        """Returns a wx.Bitmap instance of the given bitmap's name if
        found in the app's resources folder."""
        full_bitmap_path = os.path.join(pathfinder.bitmap_path(), bitmap_name)
        if os.path.exists(full_bitmap_path):
            return wx.Bitmap(name=full_bitmap_path, type=wx.BITMAP_TYPE_PNG)
        return None

    def set_thumb(self, panel, data_file, enable=True):
        """Sets the bitmap contents of the specified panel to a thumbnail
        plot of the selected data file, or a placeholder bitmap if thumbnails
        are disabled."""
        if enable:
            panel.plot_thumb(data_file)
        else:
            panel.plot_blank()

    # Event Handlers

    def on_quit(self, evt):
        """Handles the Quit event"""
        self.view._mgr.UnInit()
        self.view.Destroy()

    def on_about(self, evt):
        """Handles the About This Program event"""
        pass

    def on_about_tri(self, evt):
        """Handles the About TRI event"""
        tri_logo = os.path.join(pathfinder.bitmap_path(), "tri_austin_logo.png")
        tri_msg = ' '.join(("Texas Research Institute Austin, Inc. (TRI/Austin) is TRI's flagship company",
                            "and conducts materials research and development projects. TRI is committed to",
                            "providing the highest quality materials science products and services."))
        about_tri_dlg = dlg.AboutDialog(parent=self.view, title="About TRI",
            msg=tri_msg,
            url="www.tri-austin.com",
            logobmp_fname=tri_logo)
        about_tri_dlg.ShowModal()
        about_tri_dlg.Destroy()

    def on_about_icons(self, evt):
        """Handles the About Icons event"""
        axialis_logo = os.path.join(pathfinder.bitmap_path(), "axialis_logo.png")
        axialis_msg = ' '.join(("Some icons courtesy Axialis Software and the",
                                "Axialis Team, and were created by",
                                "Axialis IconWorkshop."))
        about_axialisicons_dlg = dlg.AboutDialog(parent=self.view, title="About Axialis Icons",
            msg=axialis_msg,
            url="www.axialis.com",
            logobmp_fname=axialis_logo)
        about_axialisicons_dlg.ShowModal()
        about_axialisicons_dlg.Destroy()

    def on_data_select(self, evt):
        """Handles a change in data file selection by providing a preview plot
        of the data"""
        self.set_thumb(panel=self.view.thumbnail_panel, data_file=self.view.data_panel.data,
            enable=self.view.toolbar.GetToolState(self.view.gen_bitmaps_tool.GetId()))
        if self.view.data_panel.data:
            self.view.enable_data_tools()
        else:
            self.view.disable_data_tools()

    def on_preview_toggle(self, evt):
        """Handles toggling data thumbnail plot previews"""
        self.set_thumb(panel=self.view.thumbnail_panel, data_file=self.view.data_panel.data,
            enable=self.view.toolbar.GetToolState(self.view.gen_bitmaps_tool.GetId()))

    def on_refresh_data(self, evt):
        """Handles request to update contents of data folder"""
        self.model.remove_thumbs()
        self.view.data_panel.populate()

    def on_add_data(self, evt):
        """Handles request to add data to data folder"""
        file_dlg = wx.FileDialog(parent=self.view.parent, message='Please specify a data file', style=wx.FD_OPEN)
        if file_dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()
            self.model.copy_data(file_dlg.GetPath())
            self.view.data_panel.populate()
            wx.EndBusyCursor()

    def on_remove_data(self, evt):
        """Handles request to remove data from data folder"""
        if self.view.data_panel.data is not None:
            confirm_deletion_dlg = wx.MessageDialog(parent=self.view.parent, caption="Delete File?",
                message="Are you sure you want to delete this file?",
                style=wx.OK | wx.CANCEL)
            if confirm_deletion_dlg.ShowModal() == wx.ID_OK:
                self.model.remove_data(self.view.data_panel.data)
                self.view.data_panel.populate()

    def on_preview_data(self, evt):
        """Handles request to preview data"""
        if self.view.data_panel.data is not None:
            import_dlg = dlg.ImportTextDialog(parent=self.view.parent)
            if import_dlg.ShowModal() == wx.ID_OK:
                read_parameters = import_dlg.get_import_parameters()
                wx.BeginBusyCursor()
                data_window = preview_window.PreviewWindow(parent=self.view, data_file=self.view.data_panel.data,
                    **read_parameters)
                data_window.Show()
                wx.EndBusyCursor()
            import_dlg.Destroy()

    def on_plot_data(self, evt):
        """Handles request to generate X-Y plot of selected data"""
        if self.view.data_panel.data is not None:
            import_dlg = dlg.ImportTextDialog(parent=self.view.parent)
            if import_dlg.ShowModal() == wx.ID_OK:
                read_parameters = import_dlg.get_import_parameters()
                wx.BeginBusyCursor()
                plt_window = plotwindow.PlotWindow(self.view, data_file=self.view.data_panel.data,
                    **read_parameters)
                if plt_window.has_data:
                    plt_window.Show()
                wx.EndBusyCursor()
            import_dlg.Destroy()

    def on_imageplot_data(self, evt):
        """Handles request to generate image plot of selected data"""
        if self.view.data_panel.data is not None:
            import_dlg = dlg.ImportTextDialog(parent=self.view.parent)
            if import_dlg.ShowModal() == wx.ID_OK:
                read_parameters = import_dlg.get_import_parameters()
                wx.BeginBusyCursor()
                plt_window = plotwindow.ImgPlotWindow(parent=self.view, data_file=self.view.data_panel.data,
                    **read_parameters)
                if plt_window.has_data:
                    plt_window.Show()
                wx.EndBusyCursor()
            import_dlg.Destroy()