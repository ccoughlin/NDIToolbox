"""dataio.py - provides functions to import and export data from various file formats commonly used in NDE

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
import numpy as np
import scipy.misc
import h5py
import gc
import itertools
import os
import os.path
import re

def get_data(data_fname, slice_idx=None):
    """Returns the NumPy array from the specified HDF5 file.  If slice_idx is specified (numpy.s_),
    returns a slice of the data rather than the entire array (default)."""
    with h5py.File(data_fname, 'r') as fidin:
        root, ext = os.path.splitext(os.path.basename(data_fname))
        for key in fidin.keys():
            if key.startswith(root):
                if slice_idx is None:
                    return fidin[key][...]
                else:
                    return fidin[key][slice_idx]

def save_data(data_fname, data):
    """Saves the data to the HDF5 file data_fname"""
    root, ext = os.path.splitext(data_fname)
    output_filename = data_fname
    hdf5_ext = '.hdf5'
    if ext.lower() != hdf5_ext:
        output_filename += hdf5_ext
    with h5py.File(output_filename, 'w') as fidout:
        fidout.create_dataset(os.path.basename(data_fname), data=data)
        gc.collect()

def get_txt_data(data_fname, **import_params):
    """Loads and returns the NumPy data from an ASCII-delimited text file"""
    comment_char = import_params.get('commentchar', '#')
    delim_char = import_params.get('delimiter', None)
    header_lines = import_params.get('skipheader', 0)
    footer_lines = import_params.get('skipfooter', 0)
    cols_to_read = import_params.get('usecols', None)
    transpose_data = import_params.get('transpose', False)
    return np.genfromtxt(data_fname, comments=comment_char, delimiter=delim_char,
                         skip_header=header_lines, skip_footer=footer_lines, usecols=cols_to_read,
                         unpack=transpose_data)

def import_txt(data_fname, **import_params):
    """Loads the data from an ASCII-delimited text file, and copies the data to a new HDF5 file in the data folder"""
    data = get_txt_data(data_fname, **import_params)
    if data is not None and data.size > 0:
        output_fname = os.path.join(pathfinder.data_path(), os.path.basename(data_fname))
        save_data(output_fname, data)

def export_txt(dest, src, **export_params):
    """Exports the NumPy array data to the text file data_fname, using the supplied export parameters."""
    delim_char = export_params.get('delimiter', None)
    newline = export_params.get('newline', '\n')
    fmt = export_params.get('format', '%f')
    data = get_data(src)
    np.savetxt(dest, data, fmt=fmt, delimiter=delim_char, newline=newline)
    gc.collect()

def get_dicom_data(data_file):
    """Returns NumPy array of DICOM/DICONDE data"""
    try:
        import dicom
        di_struct = dicom.read_file(data_file)
        return di_struct.pixel_array
    except ImportError as err: # pydicom not installed
        raise ImportError("pydicom module not installed.")

def import_dicom(data_file):
    """Imports a DICOM/DICONDE pixel map"""
    data = get_dicom_data(data_file)
    if data is not None and data.size > 0:
        di_fname = os.path.join(pathfinder.data_path(),
                                os.path.basename(data_file))
        save_data(di_fname, data)

def get_img_data(data_file, flatten=True):
    """Retrieves NumPy array of image data, by default flattening the image to a single layer grayscale."""
    return scipy.misc.imread(data_file, flatten)

def import_img(data_file, flatten=True):
    """Imports an image file, by default flattening the image to a single layer grayscale."""
    img_arr = get_img_data(data_file, flatten)
    if img_arr is not None and img_arr.size > 0:
        img_fname = os.path.join(pathfinder.data_path(), os.path.basename(data_file))
        save_data(img_fname, img_arr)

def get_utwin_tof_data(data_file):
    """Convenience function to create a UTWinCScanReader instance and return the Time Of Flight data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCscanReader(data_file)
    return scan_reader.get_tof_data()

def import_utwin_tof(data_file):
    """Convenience function to create a UTWinCScanReader instance and import the Time Of Flight data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCscanReader(data_file)
    scan_reader.import_tof()

def get_utwin_amp_data(data_file):
    """Convenience function to create a UTWinCScanReader instance and return the amplitude data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCscanReader(data_file)
    return scan_reader.get_amp_data()

def import_utwin_amp(data_file):
    """Convenience function to create a UTWinCScanReader instance and import the amplitude data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCscanReader(data_file)
    scan_reader.import_amp()

def import_utwin(data_file):
    """Convenience function to create a UTWinCScanReader instance and import the Time Of Flight, amplitude, and waveform
    data from data_file.  Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCscanReader(data_file)
    scan_reader.import_amp()
    scan_reader.import_tof()
    scan_reader.import_waveform()

def get_utwin_waveform_data(data_file):
    """Convenience function to create a UTWinCScanReader instance and return the waveform data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCscanReader(data_file)
    return scan_reader.get_waveform_data()

def import_utwin_waveform(data_file):
    """Convenience function to create a UTWinCScanReader instance and import the waveform data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCscanReader(data_file)
    scan_reader.import_waveform()

def get_winspect_data(data_file):
    """Convenience function to create a WinspectReader instance and return the waveform data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = WinspectReader(data_file)
    return scan_reader.get_winspect_data()

def import_winspect(data_file):
    """Convenience function to create a WinspectReader instance and import the data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = WinspectReader(data_file)
    scan_reader.import_winspect()

class UTWinCscanReader(object):
    """Handles reading UTWin CScan (.csc) files"""

    header_string_length = 15 # Length of header string in standard file

    # Identities of message IDs we're interested in
    message_ids = {'CSCAN_DATA':2300,
                   'WAVEFORM':2013,
                   'UTSAVE_UTCD0':2010,
                   'UTSAVE_UTCD1':2011,
                   'UTSAVE_UTCD2':2012,
                   'UTSAVE_UTCD3':2013,
                   'UTSAVE_UTCD4':2014,
                   'UTSAVE_UTPro0':253,
                   'PROJECT':301}

    def __init__(self, cscan_file):
        self.file_name = cscan_file

    def msg_info(self, file_hdl):
        """Returns a tuple of message ID and message length read from the file.  Returns (None, 0) if ID and length
        were not found."""
        msg_id = None
        msg_len = 0
        raw_msg_id = np.fromfile(file_hdl, np.int16, 1)
        raw_msg_len = np.fromfile(file_hdl, np.int32, 1)
        try:
            if raw_msg_id is not None:
                msg_id = raw_msg_id[0]
            if raw_msg_len is not None:
                msg_len = raw_msg_len[0]
        except IndexError: # one or both of message ID or length not found
            pass
        return msg_id, msg_len

    def find_message(self, message_id):
        """Returns the position in the UTWin file corresponding to the specified message ID.
        Returns -1 if message ID not found in the file."""
        with open(self.file_name, "rb") as fidin:
            fidin.seek(self.header_string_length)
            msg_id, msg_len = self.msg_info(fidin)
            while msg_id != message_id:
                fidin.read(msg_len-4)
                msg_id, msg_len = self.msg_info(fidin)
                if msg_id is None or msg_len == 0:
                    return -1
            return fidin.tell()

    def read_utcd0(self):
        """Returns a dict of the parameters read for the UTSAVE_UTCD0 message block.  Returns None if unable to read file.

        Keynames and explanation:

        n_width : Column number
        n_height : Row number
        rf_len : RF waveform length
        rf_start : RF start position (microseconds)
        rf_end : F end position (microseconds)
        rf_dt : RF period (microseconds)
        tof_res : TOF Resolution

        """
        start_pos = self.find_message(self.message_ids['UTSAVE_UTCD0'])
        if start_pos != -1:
            with open(self.file_name, "rb") as fidin:
                fidin.seek(start_pos)
                # Parameters of Cscan
                n_width = np.fromfile(fidin, np.int32, 1)[0] # Column number
                n_height = np.fromfile(fidin, np.int32, 1)[0] # Row number
                rf_len = np.fromfile(fidin, np.int32, 1)[0] # RF waveform length
                rf_start = np.fromfile(fidin, np.float32, 1)[0] # RF start position (microseconds)
                rf_end = np.fromfile(fidin, np.float32, 1)[0] # RF end position (microseconds)
                rf_dt = np.fromfile(fidin, np.float32, 1)[0] # RF period (microseconds)
                tof_res = np.fromfile(fidin, np.float32, 1)[0] # TOF Resolution
                return {'n_width':n_width,
                        'n_height':n_height,
                        'rf_len':rf_len,
                        'rf_start':rf_start,
                        'rf_end':rf_end,
                        'rf_dt':rf_dt,
                        'tof_res':tof_res}
        return None

    def read_utcd4(self):
        """Returns a dict of the parameters read for the UTSAVE_UTCD4 message block, used to store information about
        the amplitude scale.  Returns None if unable to read file.

        Keynames and explanation:

        amp_scale : Amplitude scale
        amp_offset : Amplitude offset
        adv_scale : ADV scale
        avd_offset : ADV offset

        """
        start_pos = self.find_message(self.message_ids['UTSAVE_UTCD4'])
        if start_pos != -1:
            with open(self.file_name, "rb") as fidin:
                fidin.seek(start_pos)
                amp_scale = np.fromfile(fidin, np.float32, 1)[0]
                amp_offset = np.fromfile(fidin, np.float32, 1)[0]
                adv_scale = np.fromfile(fidin, np.float32, 1)[0]
                adv_offset = np.fromfile(fidin, np.float32, 1)[0]
                return {'amp_scale':amp_scale,
                        'amp_offset':amp_offset,
                        'adv_scale':adv_scale,
                        'adv_offset':adv_offset}
        return None

    def get_tof_data(self):
        """Returns a NumPy array of the Time Of Flight data from the UTWin Cscan file file_name, or None if data could
        not be read."""
        tof_data = None
        start_pos = self.find_message(self.message_ids['UTSAVE_UTCD1'])
        scan_params = self.read_utcd0()
        if start_pos != -1 and scan_params is not None:
            with open(self.file_name, "rb") as file_hdl:
                file_hdl.seek(start_pos)
                gate = np.fromfile(file_hdl, np.uint16, 1)[0]
                tof_start = np.fromfile(file_hdl, np.float32, 1)[0]
                nsize = np.fromfile(file_hdl, np.int32, 1)[0]
                tof_data = np.fromfile(file_hdl, count=nsize, dtype=np.uint16)
                tof_data = np.reshape(tof_data, (scan_params['n_height'], scan_params['n_width']))
        return tof_data

    def import_tof(self):
        """Reads the Time Of Flight data from the CScan file and saves as a new HDF5 file in the default data folder."""
        tof_data = self.get_tof_data()
        if tof_data is not None and tof_data.size > 0:
            output_basename, ext = os.path.splitext(self.file_name)
            output_fname = os.path.join(pathfinder.data_path(), os.path.basename(output_basename)+"_tofdata"+ext)
            save_data(output_fname, tof_data)

    def get_amp_data(self):
        """Returns a NumPy array of the amplitude data from the UTWin Cscan file file_name, or None if data could not
        be read."""
        amp_data = None
        start_pos = self.find_message(self.message_ids['UTSAVE_UTCD2'])
        scan_params = self.read_utcd0()
        if start_pos != -1 and scan_params is not None:
            with open(self.file_name, "rb") as file_hdl:
                file_hdl.seek(start_pos)
                gate = np.fromfile(file_hdl, np.uint16, 1)[0]
                nsize = np.fromfile(file_hdl, np.int32, 1)[0]
                amp_data = np.fromfile(file_hdl, np.int16, count=nsize)
                amp_data = np.reshape(amp_data, (scan_params['n_height'], scan_params['n_width']))
        return amp_data

    def import_amp(self):
        """Reads the amplitude data from the CScan file and saves as a new HDF5 file in the default data folder."""
        amp_data = self.get_amp_data()
        if amp_data is not None and amp_data.size > 0:
            output_basename, ext = os.path.splitext(self.file_name)
            output_fname = os.path.join(pathfinder.data_path(), os.path.basename(output_basename)+"_ampdata"+ext)
            save_data(output_fname, amp_data)

    def get_waveform_data(self):
        """Returns a NumPy array of the waveform data from the UTWin Cscan file file_name, or None if data could not
        be read."""
        waveform_data = None
        start_pos = self.find_message(self.message_ids['WAVEFORM'])
        scan_params = self.read_utcd0()
        if start_pos != -1 and scan_params is not None:
            with open(self.file_name, "rb") as file_hdl:
                file_hdl.seek(start_pos)
                rf_size = np.fromfile(file_hdl, np.int32, 1)
                width = scan_params['n_width']
                height = scan_params['n_height']
                length = scan_params['rf_len']
                assert rf_size==(width*height*length)
                waveform_data = np.fromfile(file_hdl, np.int16, count=rf_size)
                waveform_data = np.reshape(waveform_data, (width, height, length))
        return waveform_data

    def import_waveform(self):
        """Reads the waveform data from the CScan file and saves as a new HDF5 file in the default data folder."""
        waveform_data = self.get_waveform_data()
        if waveform_data is not None and waveform_data.size > 0:
            output_basename, ext = os.path.splitext(self.file_name)
            output_fname = os.path.join(pathfinder.data_path(), os.path.basename(output_basename)+"_waveformdata"+ext)
            save_data(output_fname, waveform_data)

    @classmethod
    def is_cscanfile(cls, file_name):
        """Returns True if the file appears to be a UTWin Cscan data file, False otherwise."""
        is_cscan = False
        with open(file_name, "rb") as fidin:
            header_string = fidin.read(cls.header_string_length)
            if "UTCSCANFILE" in header_string:
                is_cscan = True
        return is_cscan

class WinspectReader(object):
    """Handles reading Winspect 6, 7 data files. Currenly only unidirectional scans are supported."""

    # Types of data stored
    data_types = ["waveform", "amplitude"]
    # Mapping element sizes to NumPy data types
    element_types = {"CHAR 8":np.int8,
                     "INTEGER 16":np.int16}
    distance_units = ["mm", "cm", "inches", "feet", "m"]
    time_units = ["Usec", "Msec"]
    signal_units = ["Volts", "%"]

    def __init__(self, scan_file):
        self.data_file = WinspectDataFile(scan_file)

    @staticmethod
    def find_numbers(option, number_type=float):
        """Parses the string option looking for numeric values (defaulting to float).  Returns a single number, a list
        of numbers if multiple values found, or [] if no numbers found.
        """
        float_regex = "[-+]?[0-9]*\.?[0-9]+"
        regex = re.compile(float_regex)
        elements = regex.findall(option)
        if len(elements) == 1:
            return number_type(elements[0])
        else:
            return [number_type(el) for el in elements]

    def get_winspect_data(self):
        """Returns the list of NumPy arrays from the data file."""
        if len(self.data_file.datasets) == 0:
            self.data_file.read_data()
        return self.data_file.datasets

    def import_winspect(self):
        """Reads and imports the Winspect data into the default data folder"""
        output_basename, ext = os.path.splitext(self.data_file.file_name)
        amp_output_fname = os.path.join(pathfinder.data_path(), os.path.basename(output_basename)+"_ampdata"+ext)
        waveform_output_fname = os.path.join(pathfinder.data_path(), os.path.basename(output_basename)+"_waveformdata"+ext)
        for dataset in self.get_winspect_data():
            if "amplitude" in dataset.data_type:
                output_fname = amp_output_fname
            elif "waveform" in dataset.data_type:
                output_fname = waveform_output_fname
            if dataset.data is not None and dataset.data.size > 0:
                save_data(output_fname, dataset.data)

class WinspectScanAxis(object):
    """WinspectReader helper class - defines the basic characteristics of a scanning axis"""

    def __init__(self, label, config):
        """Creates the configuration of the scanning axis.  The label parameter is a simple string to name this
        particular axis, and config is a dict containing the configuration parameters from the data file header.  The
        following values are read from the dict:

          Number of Sample Points : self.sample_points (int)
          Minimum Sample Position : self.minimum_position (float)
          Sample Resolution       : self.resolution (float)

        The self.units str is set according to the units of measurement specified in the Sample Resolution entry.  The
        possible values of self.units is taken from WinspectReader's distance_units from this module, e.g. one of
        ["mm", "cm", "inches", "feet", "m"].
        """
        self.label = label.title()
        self.init_config(config)

    def init_config(self, config):
        """Sets the configuration of this scanning axis according to the supplied arguments."""
        self.sample_points = WinspectReader.find_numbers(config.get("Number Of Sample Points", "0"), int)
        self.minimum_position = WinspectReader.find_numbers(config.get("Minimum Sample Position", "0"))
        self.resolution = WinspectReader.find_numbers(config.get("Sample Resolution", "0"))
        self.units = None
        for unit_type in WinspectReader.distance_units:
            if unit_type in config.get("Sample Resolution"):
                self.units = unit_type
                break

class WinspectDataSubset(object):
    """WinspectReader helper class - defines the basic characteristics of a data subset"""

    def __init__(self, parent, label, config):
        """Creates the configuration of the data subset.  The parent parameter is a link to the DataFile instance that
        owns this data subset and is used to get information about the scanning axes used in the scan.

        The label parameter is a simple string to name this particular dataset, and config is a dict containing the
        configuration parameters from the data file header.  The following values are read from the dict:

          Subset Label                     : self.data_type (str)
          Element Representation           : self.element_type (NumPy dtype)
          Number of Sample Points          : self.sample_points (int)
          Minimum Sample Position          : self.minimum_position (float)
          Sample Resolution                : self.resolution (float)
          Measurement Range                : self.measurement_range (list of floats)

        self.measurement_units is a str taken from the units used in the Measurement Range entry, and can take any of
        the values listed in WinspectReader's signal_units global list, e.g. one of ["Volts"].

        self.time_units is a str taken from the units used in the Sample Resolution entry, and can take any of the
        values listed in WinspectReader's time_units, e.g. one of ["Usec", "Msec"].

        self.data is intialized as None.  When the DataSubset's DataFile parent reads sensor data, self.data is
        reshaped as a NumPy array with shape (x0, x1, x2, ..., xi, self.sample_points) where xi is the number of sample
        points for the scan's ith axis.

        For example, a waveform scan in two axes with 760 sample points in the first axis, 220 sample points in the
        second axis, and 3500 sample points per position will create an array of shape (760, 220, 3500) with
        585,200,000 points in total.
        """
        self.label = label.title()
        self.parent = parent
        self.init_config(config)
        self.data = None
        self.set_shape()

    def init_config(self, config):
        """Sets the configuration of this subset according to the supplied arguments."""
        self.data_type = None
        for unit_type in WinspectReader.data_types:
            if unit_type in config.get("Subset Label").lower():
                self.data_type = config.get("Subset Label").lower()
                break
        self.element_type = None
        for element_type in WinspectReader.element_types:
            if element_type in config.get("Element Representation"):
                self.element_type = WinspectReader.element_types[element_type]
        self.sample_points = WinspectReader.find_numbers(config.get("Number Of Sample Points", "0"), int)
        # If we haven't yet determined what type of data is in this subset, try to set it according to the number
        # of sample points
        if self.data_type is None:
            if self.sample_points > 1:
                self.data_type = "waveform"
            else:
                self.data_type = "amplitude"
        self.minimum_position = WinspectReader.find_numbers(config.get("Minimum Sample Position", "0"))
        self.resolution = WinspectReader.find_numbers(config.get("Sample Resolution", "0"))
        self.measurement_range = WinspectReader.find_numbers(config.get("Measurement Range"))
        self.measurement_units = None
        for unit_type in WinspectReader.signal_units:
            if unit_type in config.get("Measurement Range"):
                self.measurement_units = unit_type
                break
        self.time_units = None
        for unit_type in WinspectReader.time_units:
            if unit_type in config.get("Sample Resolution"):
                self.time_units = unit_type
                break

    def num_points(self):
        """Returns the number of samples this data subset should contain."""
        return self.sample_points*reduce(lambda x,y:x*y,
                                         itertools.chain([axis.sample_points for axis in self.parent.axes]))

    def init_data(self):
        """Initializes the data array"""
        self.set_shape()
        self.data = np.zeros(shape=self.array_shape)

    def set_shape(self):
        """Sets the proper shape of the data array according to the information laid out in the file header."""
        self.array_shape = [self.parent.axes[1].sample_points, self.parent.axes[0].sample_points]
        if self.sample_points > 1:
            self.array_shape.append(self.sample_points)

    def set_data(self, raw_data):
        """Sets the data subset's data.  The raw_data NumPy array is reshaped so that it has the number of dimensions
         detailed in the file header for this particular data subset."""
        self.data = raw_data.reshape(self.array_shape)

class WinspectDataFile(object):
    """WinspectReader helper class - defines the Winspect data file"""

    def __init__(self, file_name):
        self.file_name = file_name
        self.axes = []
        self.datasets = []
        self._data_offset = 0

    def num_axes(self):
        """Returns the number of scanning axes in the data file."""
        return len(self.axes)

    def num_datasets(self):
        """Returns the number of data subsets in the data file."""
        return len(self.datasets)

    def read_header(self):
        """Reads the file header in the data file and configures the scanning axes and data subsets accordingly."""
        with open(self.file_name, "rb") as fidin:
            header_line = fidin.readline()
            config = {}
            in_sections = False
            # Read the axes and data subset configurations
            while True:
                if ":" in header_line:
                    if in_sections:
                        tokens = header_line.split(":")
                        config[tokens[0].strip().title()] = tokens[1].strip()
                else:
                    if in_sections:
                        self.add_section(section, config)
                        config = {}
                    section = header_line.lower().strip()
                    in_sections = True
                header_line = fidin.readline()
                if "|^AS Header^|" in header_line:
                    self.add_section(section, config)
                    break
            # Find the start of the data
            while True:
                if "|^Data Set^|" in header_line:
                    self._data_offset = fidin.tell()
                    break
                header_line = fidin.readline()

    def read_data(self):
        """Reads the binary data in the data file and populates the data subsets."""
        self.read_header()
        with open(self.file_name, "rb") as fidin:
            fidin.seek(self._data_offset)
            for dataset in self.datasets:
                raw_data = np.fromfile(fidin, dtype=dataset.element_type,
                                       count=dataset.num_points())
                dataset.set_data(raw_data)

    def add_section(self, section_name, config):
        """Reads the section name and creates a new WinspectScanAxis or WinspectDataSubset with the supplied config."""
        if "axis" in section_name:
            self.axes.append(WinspectScanAxis(section_name, config))
        elif "subset" in section_name:
            self.datasets.append(WinspectDataSubset(self, section_name, config))