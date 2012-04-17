""" mainui_ctrl.py - controller for mainui

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import mainmodel
from models import workerthread
import views.plotwindow as plotwindow
import views.preview_window as preview_window
import views.dialogs as dlg
from views import podtk
import controllers.pathfinder as pathfinder
import wx
import imp
import os.path
import Queue
import sys

class MainUIController(object):
    """Controller for the main user interface"""

    def __init__(self, view):
        self.view = view
        self.init_model()

    def init_model(self):
        """Creates and connects the model, ensures data paths are available"""
        self.model = mainmodel.MainModel(self)

    def verify_userpath(self):
        """Ensures the user's data folder is available"""
        if not os.path.exists(pathfinder.user_path()):
            self.set_userpath()
        self.model.check_user_path()
        self.model.copy_system_plugins()

    def verify_imports(self):
        """Ensures third-party dependencies are installed; shows
        error dialog and exits if a module is missing."""
        dependencies = ['h5py', 'dicom', 'matplotlib', 'numpy', 'scipy']
        for module in dependencies:
            try:
                imp.find_module(module)
            except ImportError: # Module not installed / not found
                msg = ' '.join(["Unable to find the '{0}' module.".format(module),
                                "Please ensure the module is installed and",
                                "restart NDIToolbox."])
                err_dlg = wx.MessageDialog(self.view, message=msg,
                                           caption="{0} Module Not Found".format(module), style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
                sys.exit(0)

    def get_icon_bmp(self):
        """Returns a PNG wx.Bitmap of the application's
        default icon"""
        icon_bmp_path = pathfinder.icon_path()
        return wx.Bitmap(icon_bmp_path, wx.BITMAP_TYPE_PNG)

    def get_icon(self):
        """Returns a wx.Icon of the application's
        default icon"""
        if sys.platform != 'win32':
            return wx.IconFromBitmap(self.get_icon_bmp())
        icon = wx.Icon(pathfinder.winicon_path(), wx.BITMAP_TYPE_ICO)
        return icon

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

    def get_default_position(self):
        """Returns the default (x, y) coordinates of the
        main application window"""
        coordinates = self.model.get_coords()
        if not coordinates:
            return (0, 0)
        return coordinates

    def get_preview_state(self):
        """Returns the current enable/disable thumbnail
        previews setting from the application's config file"""
        preview_state = self.model.get_preview_state()
        if preview_state is None:
            return True
        return preview_state

    # Event Handlers

    def on_quit(self, evt):
        """Handles the Quit event"""
        self.model.set_coords(list(self.view.GetPosition()))
        self.view._mgr.UnInit()
        self.view.Destroy()

    def on_about(self, evt):
        """Handles the About This Program event"""
        project_logo = os.path.join(pathfinder.icons_path(), 'a7117_256.png')
        project_msg = ' '.join(
            ("NDIToolbox (TM) Copyright (c) 2012 TRI/Austin, Inc.  Developed under TRI Project A7117.",
             "\n\nUse of this software is governed by the terms outlined in the license.txt file.",
             "\n\nProject Manager:  David Forsyth",
             "\nLead Developer:  Chris Coughlin")
        )
        about_project_logo_dlg = dlg.AboutDialog(parent=self.view, title="About This Program",
                                                 msg=project_msg, url="www.nditoolbox.com", logobmp_fname=project_logo)
        about_project_logo_dlg.ShowModal()
        about_project_logo_dlg.Destroy()

    def on_about_license(self, evt):
        """Handles the License Information event"""
        license_file = os.path.join(pathfinder.app_path(), 'license.txt')
        with open(license_file, 'rb') as fidin:
            license = fidin.readlines()
            license_dlg = dlg.TextDisplayDialog(parent=self.view, text=''.join(license),
                                                title="License Information")
            license_dlg.Show()

    def on_about_tri(self, evt):
        """Handles the About TRI event"""
        tri_logo = os.path.join(pathfinder.bitmap_path(), "tri_austin_logo.png")
        tri_msg = ' '.join(
            ("Texas Research Institute Austin, Inc. (TRI/Austin) is TRI's flagship company",
             "and conducts materials research and development projects.\n\nTRI is committed to",
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
        preview_state = self.view.toolbar.GetToolState(self.view.gen_bitmaps_tool.GetId())
        if preview_state:
            self.set_thumb(panel=self.view.thumbnail_panel, data_file=self.view.data_panel.data,
                           enable=preview_state)
        self.view.enable_preview_panel(preview_state)
        self.model.set_preview_state(preview_state)

    def on_refresh_data(self, evt):
        """Handles request to update contents of data folder"""
        self.refresh_data()

    def refresh_data(self):
        """Instructs UI to update list of data folder contents"""
        self.model.remove_thumbs()
        self.view.data_panel.populate()

    def on_add_data(self, evt):
        """Handles request to add data to data folder"""
        file_dlg = wx.FileDialog(parent=self.view.parent, message='Please specify a data file',
                                 style=wx.FD_OPEN)
        if file_dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()
            self.model.copy_data(file_dlg.GetPath())
            self.view.data_panel.populate()
            wx.EndBusyCursor()

    def on_choose_userpath(self, evt):
        """Handles request to set the default userpath"""
        self.set_userpath()

    def set_userpath(self):
        """ Prompts user to set a default path for storing user data """
        try:
            current_user_path = pathfinder.user_path()
            path_dlg = wx.DirDialog(parent=self.view.parent, message="Please specify a data folder",
                                    defaultPath=current_user_path)
            if path_dlg.ShowModal() == wx.ID_OK:
                new_user_path = path_dlg.GetPath()
                self.model.migrate_user_path(new_user_path)
                self.refresh_data()
        finally:
            path_dlg.Destroy()

    def on_import_text(self, evt):
        """Handles request to add ASCII data to data folder"""
        file_dlg = wx.FileDialog(parent=self.view, message="Please specify a data file",
                                 style=wx.FD_OPEN)
        if file_dlg.ShowModal() == wx.ID_OK:
            try:
                import_dlg = dlg.ImportTextDialog(parent=self.view.parent)
                if import_dlg.ShowModal() == wx.ID_OK:
                    read_parameters = import_dlg.get_import_parameters()
                    wx.BeginBusyCursor()
                    exception_queue = Queue.Queue()
                    imp_text_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                                             target=self.model.import_txt,
                                                             args=(file_dlg.GetPath(),), kwargs=read_parameters)
                    imp_text_thd.start()
                    while True:
                        imp_text_thd.join(0.125)
                        if not imp_text_thd.is_alive():
                            try:
                                exc_type, exc = exception_queue.get(block=False)
                                err_msg = "An error occurred during import:\n{0}".format(exc)
                                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                                           caption="Unable To Import File", style=wx.ICON_ERROR)
                                err_dlg.ShowModal()
                            except Queue.Empty:
                                pass
                            break
                        wx.GetApp().Yield()
                    self.view.data_panel.populate()
            finally:
                import_dlg.Destroy()
                wx.EndBusyCursor()

    def on_export_text(self, evt):
        """Handels request to export selected data to delimited ASCII"""
        file_dlg = wx.FileDialog(parent=self.view, message="Please specify a data file",
                                 style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if file_dlg.ShowModal() == wx.ID_OK:
            exportfmt_dlg = dlg.ExportTextDialog(parent=self.view.parent)
            if exportfmt_dlg.ShowModal() == wx.ID_OK:
                wx.BeginBusyCursor()
                export_params = exportfmt_dlg.get_export_parameters()
                exception_queue = Queue.Queue()
                export_text_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                                            target=self.model.export_txt,
                                                            args=(file_dlg.GetPath(), self.view.data_panel.data),
                                                            kwargs=export_params)
                export_text_thd.start()
                while True:
                    export_text_thd.join(0.125)
                    if not export_text_thd.is_alive():
                        try:
                            exc_type, exc = exception_queue.get(block=False)
                            err_msg = "An error occurred during export:\n{0}".format(exc)
                            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                                       caption="Unable To Export File", style=wx.ICON_ERROR)
                            err_dlg.ShowModal()
                        except Queue.Empty:
                            pass
                        break
                    wx.GetApp().Yield()
                wx.EndBusyCursor()
            exportfmt_dlg.Destroy()

    def on_import_dicom(self, evt):
        """Handles request to add DICOM/DICONDE data to data folder"""
        file_dlg = wx.FileDialog(parent=self.view.parent, message='Please specify a data file',
                                 style=wx.FD_OPEN)
        if file_dlg.ShowModal() == wx.ID_OK:
            try:
                wx.BeginBusyCursor()
                exception_queue = Queue.Queue()
                imp_dicom_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                                          target=self.model.import_dicom,
                                                          args=(file_dlg.GetPath(), ))
                imp_dicom_thd.start()
                while True:
                    imp_dicom_thd.join(0.125)
                    if not imp_dicom_thd.is_alive():
                        try:
                            exc_type, exc = exception_queue.get(block=False)
                            err_msg = "An error occurred during import:\n{0}".format(exc)
                            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                                       caption="Unable To Import File", style=wx.ICON_ERROR)
                            err_dlg.ShowModal()
                        except Queue.Empty:
                            pass
                        break
                    wx.GetApp().Yield()
                self.view.data_panel.populate()
            except TypeError: # 3D array not implemented
                err_dlg = wx.MessageDialog(self.view,
                                           message="3D Arrays are not supported in this version.",
                                           caption="Unable To Import Data", style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
            finally:
                wx.EndBusyCursor()

    def on_remove_data(self, evt):
        """Handles request to remove data from data folder"""
        if self.view.data_panel.data is not None:
            confirm_deletion_dlg = wx.MessageDialog(parent=self.view.parent,
                                                    caption="Delete File?",
                                                    message="Are you sure you want to delete this"\
                                                            " file?",
                                                    style=wx.OK | wx.CANCEL)
            if confirm_deletion_dlg.ShowModal() == wx.ID_OK:
                self.model.remove_data(self.view.data_panel.data)
                self.view.data_panel.populate()

    def on_preview_data(self, evt):
        """Handles request to preview data"""
        if self.view.data_panel.data is not None:
            wx.BeginBusyCursor()
            data_window = preview_window.PreviewWindow(parent=self.view,
                                                       data_file=self.view.data_panel.data)
            data_window.Show()
            wx.EndBusyCursor()


    def on_plot_data(self, evt):
        """Handles request to generate X-Y plot of selected data"""
        if self.view.data_panel.data is not None:
            wx.BeginBusyCursor()
            plt_window = plotwindow.PlotWindow(self.view, data_file=self.view.data_panel.data)
            if plt_window.has_data:
                plt_window.Show()
            wx.EndBusyCursor()

    def on_imageplot_data(self, evt):
        """Handles request to generate image plot of selected data"""
        if self.view.data_panel.data is not None:
            wx.BeginBusyCursor()
            plt_window = plotwindow.ImgPlotWindow(parent=self.view,
                                                  data_file=self.view.data_panel.data)
            if plt_window.has_data:
                plt_window.Show()
            wx.EndBusyCursor()

    def on_run_podtk(self, evt):
        """Handles request to run POD Toolkit"""
        podtk_ui = podtk.PODWindow(parent=self.view)
        podtk_ui.Show()