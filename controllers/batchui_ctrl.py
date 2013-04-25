"""batchui_ctrl.py - controller for the console batch processing mode

Chris R. Coughlin (TRI/Austin, Inc.)
"""

import pathfinder
from models import mainmodel
from models import dataio
import json
import os.path

# Currently supported filetypes - keys are the names of the file formats supported, values are
# lists of expected file extensions
file_types = {'nditoolbox':['.hdf5'],
              'winspect':['.sdt'],
              'utwin':['.csc'],
              'dicom':['.dcm'],
              'image':['.bmp', '.dcx', '.eps', '.gif', '.im', '.imt', '.jpg', '.jpeg', '.pcx',
                       '.png', '.ppm', '.psd', '.sgi', '.tga', '.tiff', '.xpm']}


def available_file_types():
    """Returns a list of the currently supported filetypes"""
    return file_types.keys()


def get_file_type(filename):
    """Returns the assumed type of NDIToolbox input file based on the provided filename's
    extension, or None if no match found."""
    root, ext = os.path.splitext(filename)
    for _t in file_types:
        if ext.lower() in file_types[_t]:
            return _t
    return None


class BatchPluginAdapter(object):
    """Adapter class for running NDIToolbox plugins in batch mode"""

    def __init__(self, toolkit, datafname, toolkit_cfg=None, filetype=None):
        self.toolkit = toolkit
        self.datafile = datafname
        self.toolkit_cfg = toolkit_cfg
        if filetype is None:
            filetype = get_file_type(datafname)
        self.filetype = filetype
        self._data = {}

    @property
    def data(self):
        """Returns the toolkit's current data, or None if no data"""
        return self._data

    def get_plugin_class(self):
        """Returns the plugin class with the specified name, or None if not found."""
        available_plugins = mainmodel.load_plugins()
        plugin_names = [plugin[0] for plugin in available_plugins]
        plugin_classes = [plugin[1] for plugin in available_plugins]
        if self.toolkit in plugin_names:
            plugin_class = plugin_classes[plugin_names.index(self.toolkit)]
        return plugin_class

    def init_toolkit(self):
        """Instantiates the NDIToolbox toolkit"""
        plugin_cls = self.get_plugin_class()
        self.toolkit_instance = plugin_cls()
        cfg_dict = {'datafile':self.datafile}
        if self.toolkit_cfg is not None:
            with open(self.toolkit_cfg, "rb") as fidin:
                cfg_dict.update(json.load(fidin))
        if hasattr(self.toolkit_instance, 'config'):
            self.toolkit_instance.config.update(cfg_dict)
        else:
            self.toolkit_instance.config = cfg_dict

    def read_data(self):
        """Reads the supplied data file based on the supplied/assumed filetype.  If filetype was
        not specified, assumes file format based on file's extension."""
        tof_counter = 0
        amp_counter = 0
        waveform_counter = 0
        if self.filetype is not None and self.filetype in available_file_types():
            if self.filetype == 'nditoolbox':
                self._data = dataio.get_data(self.datafile)
            if self.filetype == 'winspect':
                raw_data = dataio.get_winspect_data(self.datafile)
                # Handle any files that may have stored multiple datasets of
                # a given type(s)
                for dataset in raw_data:
                    dataset_key = os.path.basename(self.datafile)
                    if dataset.data_type == 'waveform':
                        dataset_key = 'waveform' + str(waveform_counter)
                        waveform_counter +=1
                    elif dataset.data_type == 'amplitude':
                        dataset_key = 'amplitude' + str(amp_counter)
                        amp_counter += 1
                    elif dataset.data_type == 'tof': #TODO -confirm SDT files use tof
                        dataset_key = 'tof' + str(tof_counter)
                        tof_counter += 1
                    self._data[dataset_key] = dataset.data
            if self.filetype == 'csv':
                self._data = dataio.get_txt_data(self.datafile)
            if self.filetype == 'image':
                self._data = dataio.get_img_data(self.datafile, flatten=True)
            if self.filetype == 'dicom':
                self._data = dataio.get_dicom_data(self.datafile)
            if self.filetype == 'utwin':
                utwin_data = dataio.get_utwin_data(self.datafile)
                self._data = {k:utwin_data[k] for k in utwin_data if utwin_data[k] is not None}

    def run(self):
        """Executes the toolkit"""
        self.init_toolkit()
        self.read_data()
        self.toolkit_instance.data = self._data
        self.toolkit_instance.run()
        self._data = self.toolkit_instance.data


def run_plugin(toolkit, input_file, toolkit_config=None, file_type=None, save_data=True):
    """Convenience function for creating and executing BatchPluginAdapters and optionally saving
    results to NDIToolbox data folder, e.g. for multiprocessing Pools.

    toolkit -           name of plugin class (NOT name of plugin file):  e.g. MedianFilterPlugin,
                        not medfilter_plugin.py.  Must be an installed NDIToolbox plugin.

    input_file -        name of the input data file.  If file_type is not specified (default),
                        type of file is assumed based on file extension.

    toolkit_config -    (optional) JSON configuration file for the toolkit.

    file_type -         (optional) specify the file format.  Must be one of the file formats
                        supported by NDIToolbox.  Currently supported: 'image', 'nditoolbox',
                        'utwin', 'csv', 'winspect', 'dicom' (use the available_file_types
                        function to retrieve a list of supported types).  If not specified,
                        format is assumed based on file extension.

    save_data -         (optional) if True, resultant data are saved to a new HDF5 data file with
                        the same basename as the input file.  Defaults to True.
    """
    batch_runner = BatchPluginAdapter(toolkit, input_file, toolkit_cfg=toolkit_config, filetype=file_type)
    batch_runner.run()
    if save_data:
        if hasattr(batch_runner.data, "keys"):
            # Handle multiple datasets
            for dataset in batch_runner.data:
                root, ext = os.path.splitext(os.path.basename(input_file))
                output_fname = os.path.join(pathfinder.batchoutput_path(), root + "_" + dataset + ".hdf5")
                dataio.save_data(output_fname, batch_runner.data[dataset])
        else:
            # Handle single dataset
            root, ext = os.path.splitext(os.path.basename(input_file))
            output_fname = os.path.join(pathfinder.batchoutput_path(), root + ".hdf5")
            dataio.save_data(output_fname, batch_runner._data)
