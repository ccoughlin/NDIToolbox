"""podtk_ctrl.py - controller for the POD Toolkit

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.podtk_model import PODWindowModel
from models import workerthread
from models.mainmodel import get_logger
from controllers import pathfinder
from views import dialogs
from views import fetchpodmodel_dialog
import wx
import Queue

module_logger = get_logger(__name__)

class PODWindowController(object):
    """Controller for the PODWindow UI"""

    def __init__(self, view):
        self.view = view
        self.model = PODWindowModel(self)
        module_logger.info("Successfully initialized PODWindowController.")

    def get_models(self):
        """Retrieves the list of PODModels
        and populates the TreeCtrl"""
        pod_models = self.model.load_models()
        for model in pod_models:
            self.view.modeltree.add_model(model)

    def get_data(self, file_name, file_type):
        """Returns the NumPy data from the specified data file.  The file_type argument
        is a str indicating the file format - currently supported are 'csv' and 'hdf5'.
        """
        if file_type.lower() == 'csv':
            load_data_fn = self.model.load_csv
        elif file_type.lower() == 'hdf5':
            load_data_fn = self.model.load_data
        return load_data_fn(file_name)

    # Event Handlers
    def on_quit(self, evt):
        """Handles Close Window request"""
        self.view.close()

    def on_download_model(self, evt):
        """Handles request to download and install a plugin"""
        dlg = fetchpodmodel_dialog.FetchRemotePODModelDialog(parent=self.view)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                dlg.install_plugin()
                self.view.modeltree.clear()
                self.get_models()
            except Exception as err:
                module_logger.error("Unable to install POD Model: {0}".format(err))
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Install POD Model",
                                           style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
        dlg.Destroy()

    def on_install_model(self, evt):
        """Handles request to install a local POD Model"""
        file_dlg = wx.FileDialog(parent=self.view,
                                 message="Please select a POD Model archive to install.",
                                 wildcard="ZIP files (*.zip)|*.zip|All files (*.*)|*.*")
        if file_dlg.ShowModal() == wx.ID_OK:
            dlg = fetchpodmodel_dialog.FetchPODModelDialog(parent=self.view,
                                                           plugin_path=file_dlg.GetPath())
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    dlg.install_plugin()
                    self.view.modeltree.clear()
                    self.get_models()
                except Exception as err:
                    module_logger.error("Unable to install POD Model: {0}".format(err))
                    err_msg = "{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Install POD Model",
                                               style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
            dlg.Destroy()
        file_dlg.Destroy()

    def on_delete_model(self, evt):
        """Handles request to delete a model"""
        # Placeholder for now
        delmodel_dlg = wx.MessageDialog(self.view, caption="Remove A POD Model",
                                        message="This feature not yet implemented.\nPlease "\
                                                "contact TRI for assistance."
                                        ,
                                        style=wx.OK | wx.ICON_INFORMATION)
        delmodel_dlg.ShowModal()
        delmodel_dlg.Destroy()

    def on_about(self, evt):
        """Handles request to show About dialog"""
        # Placeholder for now
        about_dlg = wx.MessageDialog(self.view, caption="About PODToolkit",
                                     message="This is the Probability Of Detection Toolkit",
                                     style=wx.OK | wx.ICON_INFORMATION)
        about_dlg.ShowModal()
        about_dlg.Destroy()

    def on_help(self, evt):
        """Handles request to show Help information"""
        # Placeholder for now
        help_dlg = wx.MessageDialog(self.view, caption="PODToolkit Help",
                                    message="This feature not yet implemented.\nPlease contact "\
                                            "TRI for assistance."
                                    ,
                                    style=wx.OK | wx.ICON_INFORMATION)
        help_dlg.ShowModal()
        help_dlg.Destroy()

    def on_selection_change(self, evt):
        """Handles selection change event in ModelTree -
        updates ModelProperty Editor"""
        item = evt.GetItem()
        if item:
            self.refresh_mpgrid(item)
        evt.Skip()

    def refresh_mpgrid(self, item):
        """Updates the ModelProperties Grid with the specified
        ModelTree item."""
        selected_obj = self.view.modeltree.GetItemPyData(item)
        if isinstance(selected_obj, dict):
            self.view.mp_lbl.SetLabel(self.view.modeltree.selectionParentLabel())
            self.view.mp_grid.ClearGrid()
            props = selected_obj.keys()
            self.view.mp_grid.SetNumberRows(len(props))
            row = 0
            for prop in props:
                self.view.mp_grid.SetCellValue(row, 0, prop)
                self.view.mp_grid.SetCellValue(row, 1, str(selected_obj.get(prop)))
                row += 1

    def on_modeltree_change(self, evt):
        """Handles changes in the ModelTree - updates ModelProperty Editor"""
        self.on_selection_change(evt)

    def on_right_click_modeltree(self, evt):
        """Handles right-click event in the ModelTree"""
        click_pos = evt.GetPosition()
        item, flags = self.view.modeltree.HitTest(click_pos)
        if item:
            self.view.modeltree.SelectItem(item)
            self.view.tree_popup(click_pos)

    def on_edit_inputdata(self, evt):
        """Handles request to load input data into worksheet"""
        input_data = self.view.modeltree.selected_inputdata()
        if input_data is not None:
            try:
                data = self.get_data(input_data['filename'], input_data['filetype'])
                self.populate_spreadsheet(self.view.input_grid, data)
            except IOError as err:
                module_logger.error("Unable to read input data: {0}".format(err))
                err_dlg = wx.MessageDialog(self.view, caption="Failed To Read File",
                                           message=str(err), style=wx.OK | wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()

    def on_choose_inputdata(self, evt):
        """Handles request to set input data file"""
        selected_input_data = self.view.modeltree.GetSelection()
        if selected_input_data.IsOk():
            file_dlg = wx.FileDialog(self.view, message="Please select a data file",
                                     wildcard="HDF5 files (*.hdf5)|*.hdf5|CSV files (*.csv)|*.csv|"\
                                              "All Files (*.*)|*.*"
                                     ,
                                     style=wx.FD_OPEN)
            if file_dlg.ShowModal() == wx.ID_OK:
                inputdata_item = self.view.modeltree.GetItemPyData(selected_input_data)
                inputdata_item['filename'] = file_dlg.GetPath()
                self.view.modeltree.SetItemPyData(selected_input_data, inputdata_item)
                self.view.modeltree.SelectItem(selected_input_data)
                self.refresh_mpgrid(selected_input_data)

    def on_sheet_tool_click(self, evt):
        """Handles toolbar button clicks in the spreadsheet -
        currently supports Open File (id=20) and Save File (id=30)."""
        if evt.GetId() == 20: # Open File
            file_dlg = wx.FileDialog(self.view, message="Please select a CSV file",
                                     wildcard="CSV files (*.csv)|*.csv|Text Files (*.txt)|*"\
                                              ".txt|All Files (*.*)|*.*"
                                     ,
                                     style=wx.FD_OPEN)
            if file_dlg.ShowModal() == wx.ID_OK:
                try:
                    grid = self.get_active_grid()
                    data = self.get_data(file_dlg.GetPath(), "csv")
                    if data is not None:
                        self.populate_spreadsheet(grid, data)
                    else:
                        raise IOError("File not recognized as CSV.")
                except Exception as err:
                    if str(err) is None:
                        msg = "An unknown error occurred attempting to read the file."
                    else:
                        msg = "An error occurred attempting to read the file:\n\n{0}".format(
                            str(err))
                    module_logger.error("Unable to read file: {0}".format(err))
                    err_dlg = wx.MessageDialog(self.view, caption="Failed To Read File",
                                               message=msg, style=wx.OK | wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
        elif evt.GetId() == 30: # Save File
            save_file_dlg = wx.FileDialog(self.view, message="Please specify an output filename",
                                          defaultDir=pathfinder.podmodels_path(),
                                          wildcard="CSV files (*.csv)|*.csv|Text Files (*.txt)|*"\
                                                   ".txt|All Files (*.*)|*.*"
                                          ,
                                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if save_file_dlg.ShowModal() == wx.ID_OK:
                grid = self.get_active_grid()
                grid.WriteCSV(save_file_dlg.GetPath())
            save_file_dlg.Destroy()

    def get_active_grid(self):
        """Returns the currently-selected Spreadsheet control from the view"""
        grid = None
        active_page = self.view.spreadsheet_nb.GetSelection()
        if active_page == 0:
            grid = self.view.input_grid
        elif active_page == 1:
            grid = self.view.output_grid
        return grid

    def on_property_change(self, evt):
        """Handles changes in ModelProperty Editor - ModelTree updated
        with new values."""
        click_pos = evt.GetPosition()
        item = self.view.mp_grid.HitTest(click_pos)
        if item:
            property_name = self.view.mp_grid.GetCellValue(evt.GetRow(), 0)
            property_value = self.view.mp_grid.GetCellValue(evt.GetRow(), 1)
            selected_property = self.view.modeltree.GetSelection()
            if selected_property.IsOk() and selected_property != self.view.modeltree.GetRootItem():
                self.view.modeltree.GetItemPyData(selected_property)[property_name] =\
                property_value

    def on_save_model(self, evt):
        """Handles request to store POD Model configuration changes to disk"""
        try:
            model = self.view.modeltree.get_model()
            if model is not None:
                model.save_configuration()
        except ValueError: # No model selected
            module_logger.error("Unable to save POD Model, no model selected.")
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                                       message="Please select a POD Model.",
                                       style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_runmodel(self, evt):
        """Handles request to execute current POD Model"""
        try:
            model = self.view.modeltree.get_model()
            if model is not None:
                self.run_model(model)
        except ValueError: # No model selected
            module_logger.error("Unable to run POD Model, no model selected.")
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                                       message="Please select a POD Model.",
                                       style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def run_model(self, model_instance):
        """Runs the specified POD Model instance in a separate thread."""
        exception_queue = Queue.Queue()
        model_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                              target=model_instance.run)
        model_thd.start()
        progress_dlg = dialogs.progressDialog(dlg_title="Running POD Model",
                                              dlg_msg="Please wait, running POD Model...")
        while True:
            model_thd.join(0.125)
            progress_dlg.update()
            if not model_thd.is_alive():
                try:
                    exc_type, exc = exception_queue.get(block=False)
                    module_logger.error("Unable to run POD Model: {0}".format(exc))
                    err_msg = "An error occurred while running the POD Model:\n{0}".format(exc)
                    err_dlg = wx.MessageDialog(self.view.parent, message=err_msg,
                                               caption="Error In POD Model Execution",
                                               style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    return
                except Queue.Empty:
                    # No errors occurred, continue processing
                    model_instance.plot1(self.view.axes1)
                    model_instance.plot2(self.view.axes2)
                    if model_instance.data is not None: # Model returned data to display
                        try:
                            self.populate_spreadsheet(self.view.output_grid, model_instance.data)
                            self.view.spreadsheet_nb.ChangeSelection(self.view.output_sheet_page)
                        except MemoryError: # File too large to load
                            module_logger.error("Unable to preview data, file too large to fit in memory.")
                            err_msg = "The file is too large to load."
                            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                                       caption="Unable To Preview Data",
                                                       style=wx.ICON_ERROR)
                            err_dlg.ShowModal()
                            err_dlg.Destroy()
                    if model_instance.results is not None: # Model return output text to display
                        self.view.txtoutput_tc.WriteText(model_instance.results)
                    self.refresh_plots()
                    break
                finally:
                    progress_dlg.close()
            wx.GetApp().Yield(True)

    def refresh_plots(self):
        """Forces update to the plots (required after some plotting commands)"""
        self.view.canvas1.draw()
        self.view.canvas2.draw()

    def populate_spreadsheet(self, spreadsheet_ctrl, data_array):
        """Clears the specified wxSpreadSheet instance and fills with
        the contents of the NumPy data_array."""
        spreadsheet_ctrl.ClearGrid()
        spreadsheet_ctrl.SetNumberRows(0)
        spreadsheet_ctrl.SetNumberCols(0)
        rownum = 0
        if data_array.ndim == 2:
            num_rows = data_array.shape[0]
            for row in range(num_rows):
                spreadsheet_ctrl.AppendRows(1)
                numcols = data_array[row].size
                if spreadsheet_ctrl.GetNumberCols() < numcols:
                    spreadsheet_ctrl.SetNumberCols(numcols)
                colnum = 0
                for cell in data_array[row]:
                    spreadsheet_ctrl.SetCellValue(rownum, colnum, str(cell))
                    colnum += 1
                rownum += 1
        elif data_array.ndim == 1:
            spreadsheet_ctrl.SetNumberCols(1)
            for el in data_array:
                spreadsheet_ctrl.AppendRows(1)
                spreadsheet_ctrl.SetCellValue(rownum, 0, str(el))
                rownum += 1