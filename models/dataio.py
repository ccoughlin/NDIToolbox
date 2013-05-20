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
    if data.ndim < 3:
        np.savetxt(dest, data, fmt=fmt, delimiter=delim_char, newline=newline)
    elif data.ndim == 3:
        # NumPy doesn't handle saving 3D data to text files, do it manually as X,Y,Z
        with open(dest, "w") as fidout:
            fidout.write("# NDIToolbox ASCII export of file '{0}'".format(os.path.basename(src)))
            fidout.write(newline)
            fidout.write("# File format: x index{0}y index{0}data value at (x, y)".format(delim_char))
            fidout.write(newline)
            if "i" in fmt:
                dtype = np.int
            else: # default to 64-bit float if no format provided
                dtype = np.float
            for xidx in range(data.shape[1]):
                for yidx in range(data.shape[0]):
                    for zidx in range(data.shape[2]):
                        z = data[yidx, xidx, zidx].astype(dtype)
                        lineout = delim_char.join([str(xidx), str(yidx), str(z)])
                        fidout.write(lineout)
                        fidout.write(newline)
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
    scan_reader = UTWinCScanDataFile(data_file)
    scan_reader.read_tof_data()
    return scan_reader.data['tof']

def import_utwin_tof(data_file):
    """Convenience function to create a UTWinCScanReader instance and import the Time Of Flight data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCScanDataFile(data_file)
    scan_reader.import_tof_data()

def get_utwin_amp_data(data_file):
    """Convenience function to create a UTWinCScanReader instance and return the amplitude data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCScanDataFile(data_file)
    scan_reader.read_amplitude_data()
    return scan_reader.data['amplitude']

def import_utwin_amp(data_file):
    """Convenience function to create a UTWinCScanReader instance and import the amplitude data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCScanDataFile(data_file)
    scan_reader.import_amplitude_data()

def import_utwin(data_file):
    """Convenience function to create a UTWinCScanReader instance and import the Time Of Flight, amplitude, and waveform
    data from data_file.  Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCScanDataFile(data_file)
    scan_reader.import_data()

def get_utwin_waveform_data(data_file):
    """Convenience function to create a UTWinCScanReader instance and return the waveform data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCScanDataFile(data_file)
    scan_reader.read_waveform_data()
    return scan_reader.data['waveform']

def import_utwin_waveform(data_file):
    """Convenience function to create a UTWinCScanReader instance and import the waveform data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCScanDataFile(data_file)
    scan_reader.import_waveform_data()

def get_utwin_data(data_file):
    """Convenience function to create a UTWinCScanReader instance and return all the data from data_file.
    Primarily intended for use in threading and multiprocessing."""
    scan_reader = UTWinCScanDataFile(data_file)
    scan_reader.read_data()
    return scan_reader.data

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
    message_ids = {'CSCAN_DATA': 2300,
                   'WAVEFORM_pre240': 2016,
                   'WAVEFORM_post240': 2303,
                   'UTSAVE_UTCD0': 2010,
                   'UTSAVE_UTCD1': 2011,
                   'UTSAVE_UTCD2': 2012,
                   'UTSAVE_UTCD4': 2014,
                   'UTSAVE_UTPro0': 253,
                   'PROJECT': 301,
                   'UTSAVE_UTHead': 100,
                   'UTSAVE_UTCScan0': 750,
                   'UTSAVE_UTCD10': 2020,
                   'UTSAVE_UTCScan3': 753}

    # Converting between UTWin field sizes and NumPy equivalents
    field_sizes = {'short': np.int16,
                   'ushort': np.uint16,
                   'int': np.int32,
                   'uint': np.uint32,
                   'float': np.float32,
                   'double': np.float64,
                   'long': np.int64,
                   'ulong': np.uint64}

    @classmethod
    def msg_info(cls, file_hdl):
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

    @classmethod
    def find_message(cls, file_name, message_id):
        """Returns the position in the UTWin file corresponding to the specified message ID.
        Returns -1 if message ID not found in the file."""
        with open(file_name, "rb") as fidin:
            fidin.seek(cls.header_string_length)
            msg_id, msg_len = cls.msg_info(fidin)
            while msg_id != message_id:
                fidin.read(msg_len-4)
                msg_id, msg_len = cls.msg_info(fidin)
                if msg_id is None or msg_len == 0:
                    return -1
            return fidin.tell()

    @classmethod
    def find_blocks(cls, file_name, message_id):
        """Returns a list of the file positions found for the specified message ID."""
        block_positions = []
        file_size = os.stat(file_name).st_size
        with open(file_name, "rb") as fidin:
            fidin.seek(cls.header_string_length)
            msg_id, msg_len = cls.msg_info(fidin)
            while fidin.tell() != file_size:
                if msg_id == message_id:
                    block_positions.append(fidin.tell())
                fidin.read(msg_len-4)
                msg_id, msg_len = cls.msg_info(fidin)
        return block_positions

    @classmethod
    def read_field(cls, file_hdl, message_size, num_blocks=1):
        """Reads a field from the specified file handle.  Returns a single
        element if num_blocks is 1 (default), or a list of elements if num_blocks >= 1."""
        field = np.fromfile(file_hdl, message_size, num_blocks)
        if num_blocks == 1:
            field = field[0]
        return field

    @classmethod
    def is_cscanfile(cls, file_name):
        """Returns True if the file appears to be a UTWin Cscan data file, False otherwise."""
        is_cscan = False
        with open(file_name, "rb") as fidin:
            header_string = fidin.read(cls.header_string_length)
            if "UTCSCANFILE" in header_string:
                is_cscan = True
        return is_cscan

class UTWinCScanDataFile(object):
    """Basic definition of a UTWin CScan data file"""

    def __init__(self, data_file):
        self.data_file = data_file
        self._data = {'waveform':[], 'amplitude':[], 'tof':[]}
        self.scan_properties = {}
        self.read_scan_properties()
        self.compression_properties = {}
        self.read_compression_properties()

    @property
    def data(self):
        return self._data

    def get_scan_version(self):
        """Returns the scan version of the data file, or -1 if unable to read."""
        scan_version = -1
        start_pos = UTWinCscanReader.find_message(self.data_file, UTWinCscanReader.message_ids['UTSAVE_UTHead'])
        if start_pos != -1:
            with open(self.data_file, "rb") as fidin:
                fidin.seek(start_pos)
                scan_version = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['ushort'])
        return scan_version

    def read_scan_properties(self):
        """Compiles various properties of the scan required to properly read the datasets"""
        start_pos = UTWinCscanReader.find_message(self.data_file, UTWinCscanReader.message_ids['UTSAVE_UTCD0'])
        if start_pos != -1:
            with open(self.data_file, "rb") as fidin:
                fidin.seek(start_pos)
                self.scan_properties['n_width'] = UTWinCscanReader.read_field(fidin,
                                                                              UTWinCscanReader.field_sizes['int'])
                self.scan_properties['n_height'] = UTWinCscanReader.read_field(fidin,
                                                                               UTWinCscanReader.field_sizes['int'])
                self.scan_properties['rf_length'] = UTWinCscanReader.read_field(fidin,
                                                                                UTWinCscanReader.field_sizes['int'])
                self.scan_properties['rf_start'] = UTWinCscanReader.read_field(fidin,
                                                                               UTWinCscanReader.field_sizes['float'])
                self.scan_properties['rf_end'] = UTWinCscanReader.read_field(fidin,
                                                                             UTWinCscanReader.field_sizes['float'])
                self.scan_properties['rf_dt'] = UTWinCscanReader.read_field(fidin,
                                                                            UTWinCscanReader.field_sizes['float'])
                self.scan_properties['tof_resolution'] = UTWinCscanReader.read_field(fidin,
                                                                                     UTWinCscanReader.field_sizes['float'])
        start_pos = UTWinCscanReader.find_message(self.data_file, UTWinCscanReader.message_ids['UTSAVE_UTCScan0'])
        if start_pos != -1:
            with open(self.data_file, "rb") as fidin:
                fidin.seek(start_pos)
                self.scan_properties['cs_scan_mode'] = UTWinCscanReader.read_field(fidin,
                                                                                   UTWinCscanReader.field_sizes['short'])
                self.scan_properties['cs_zscan_mode'] = UTWinCscanReader.read_field(fidin,
                                                                                    UTWinCscanReader.field_sizes['short'])
                self.scan_properties['cs_zindex_mode'] = UTWinCscanReader.read_field(fidin,
                                                                                     UTWinCscanReader.field_sizes['short'])
                self.scan_properties['cs_scan_length'] = UTWinCscanReader.read_field(fidin,
                                                                                     UTWinCscanReader.field_sizes['double'])
                self.scan_properties['cs_scan_resolution'] = UTWinCscanReader.read_field(fidin,
                                                                                         UTWinCscanReader.field_sizes['double'])
                self.scan_properties['cs_scan_speed'] = UTWinCscanReader.read_field(fidin,
                                                                                    UTWinCscanReader.field_sizes['double'])
                self.scan_properties['cs_index_length'] = UTWinCscanReader.read_field(fidin,
                                                                                      UTWinCscanReader.field_sizes['double'])
                self.scan_properties['cs_index_resolution'] = UTWinCscanReader.read_field(fidin,
                                                                                          UTWinCscanReader.field_sizes['double'])
                self.scan_properties['cs_index_speed'] = UTWinCscanReader.read_field(fidin,
                                                                                     UTWinCscanReader.field_sizes['double'])
                self.scan_properties['cs_jog_length'] = UTWinCscanReader.read_field(fidin,
                                                                                    UTWinCscanReader.field_sizes['double'])
                self.scan_properties['cs_jog_resolution'] = UTWinCscanReader.read_field(fidin,
                                                                                        UTWinCscanReader.field_sizes['double'])
                self.scan_properties['cs_jog_speed'] = UTWinCscanReader.read_field(fidin,
                                                                                   UTWinCscanReader.field_sizes['double'])
                self.scan_properties['num_axes'] = UTWinCscanReader.read_field(fidin,
                                                                               UTWinCscanReader.field_sizes['ushort'])
                self.scan_properties['axes'] = []
                for i in range(self.scan_properties['num_axes']):
                    axis_start_pos = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['double'])
                    axis_start_sequence = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                    self.scan_properties['axes'].append({'start_pos':axis_start_pos,
                                                         'start_sequence':axis_start_sequence})
                self.scan_properties['num_channels'] = UTWinCscanReader.read_field(fidin,
                                                                                   UTWinCscanReader.field_sizes['int'])
                self.scan_properties['channel_active'] = []
                for i in range(self.scan_properties['num_channels']):
                    self.scan_properties['channel_active'].append(UTWinCscanReader.read_field(fidin,
                                                                                              UTWinCscanReader.field_sizes['short']))

    def read_compression_properties(self):
        """Compiles various properties of the waveform compression required to properly read the datasets."""
        start_pos = UTWinCscanReader.find_message(self.data_file, UTWinCscanReader.message_ids['UTSAVE_UTCD10'])
        if start_pos != -1:
            with open(self.data_file, "rb") as fidin:
                fidin.seek(start_pos)
                self.compression_properties['is_waveform_compressed'] = UTWinCscanReader.read_field(fidin,
                                                                                                    UTWinCscanReader.field_sizes['short'])
                self.compression_properties['is_8bit_data'] = UTWinCscanReader.read_field(fidin,
                                                                                          UTWinCscanReader.field_sizes['short'])
                self.compression_properties['compression_method'] = UTWinCscanReader.read_field(fidin,
                                                                                                UTWinCscanReader.field_sizes['short'])
                self.compression_properties['compression_ratio'] = UTWinCscanReader.read_field(fidin,
                                                                                               UTWinCscanReader.field_sizes['double'])
                self.compression_properties['compression_bit'] = UTWinCscanReader.read_field(fidin,
                                                                                             UTWinCscanReader.field_sizes['int'])
                self.compression_properties['compressed_rf_length'] = UTWinCscanReader.read_field(fidin,
                                                                                                  UTWinCscanReader.field_sizes['int'])
                self.compression_properties['is_threshold_compressed'] = self.read_compression_properties753()['is_threshold_compressed']

    def read_compression_properties753(self):
        """Reads additional compression properties from block #753"""
        start_pos = UTWinCscanReader.find_message(self.data_file, UTWinCscanReader.message_ids['UTSAVE_UTCScan3'])
        if start_pos != -1:
            with open(self.data_file, "rb") as fidin:
                fidin.seek(start_pos)
                is_waveform_compressed = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                compression_method = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                compression_ratio = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['double'])
                is_8bit_data = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                is_threshold_compressed = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                compression_width_1 = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                compression_width_2 = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                soft_backlash = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['double'])
                compression_threshold = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['double'])
                compression_offset_1 = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                compression_offset_2 = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'])
                compressed_rf_length = self.calculate_compressed_waveform_size()
                return {'is_waveform_compressed':is_waveform_compressed,
                        'compression_method':compression_method,
                        'compression_ratio':compression_ratio,
                        'is_8bit_data':is_8bit_data,
                        'is_threshold_compressed':is_threshold_compressed,
                        'compression_width_1':compression_width_1,
                        'compression_width_2':compression_width_2,
                        'soft_backlash':soft_backlash,
                        'compression_threshold':compression_threshold,
                        'compression_offset_1':compression_offset_1,
                        'compression_offset_2':compression_offset_2,
                        'compressed_rf_length':compressed_rf_length}

    def calculate_compressed_waveform_size(self):
        """Calculates and returns the size of the compressed waveform"""
        dk = int(self.compression_properties['compression_ratio'])
        if dk <= 0 or self.compression_properties['compression_method'] == 0:
            dk = 1
        if self.compression_properties['is_8bit_data']:
            compressed_waveform_length = int(float(self.scan_properties['rf_length']) / float(dk) / 2 + 0.5) + 2
        else:
            compressed_waveform_length = int(float(self.scan_properties['rf_length']) / float(dk) + 0.5) + 2
        if compressed_waveform_length > self.scan_properties['rf_length']:
            compressed_waveform_length = self.scan_properties['rf_length']
        return compressed_waveform_length

    def read_data(self):
        """Reads the Time Of Flight (TOF), amplitude, and waveform datasets from the UTWin data file.
        Populates the self._data dict with lists of the datasets:

        self._data['tof']           : list of TOF datasets
        self._data['amplitude']     : list of amplitude datasets
        self._data['waveform']      : list of waveform datasets
        """
        self.read_tof_data()
        self.read_amplitude_data()
        self.read_waveform_data()

    def import_data(self):
        """Reads the Time Of Flight (TOF), amplitude, and waveform datasets from the UTWin data file, and
        exports a copy of each dataset as an HDF5 file.
        """
        self.import_tof_data()
        self.import_amplitude_data()
        self.import_waveform_data()

    def read_waveform_data(self):
        """Reads the waveform datasets from the UTWin data file."""
        if self.get_scan_version() >= 240:
            # File format for waveform storage changed after UTWin v. 2.40
            self.read_waveform_data_post240()
        else:
            self.read_waveform_data_pre240()

    def read_waveform_data_post240(self):
        """Reads the waveform datasets from UTWin files, version 2.40+"""
        waveforms = []
        waveform_positions = UTWinCscanReader.find_blocks(self.data_file, UTWinCscanReader.message_ids['WAVEFORM_post240'])
        with open(self.data_file, "rb") as fidin:
            for pos in waveform_positions:
                fidin.seek(pos)
                index = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['int'])
                for idx in range(sum(self.scan_properties['channel_active'])):
                    if self.scan_properties['channel_active'][idx] == 1:
                        rf_line_length = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['int'])
                        waveform_data = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'],
                                                                    rf_line_length)
                        if self.compression_properties['is_waveform_compressed']:
                            waveform_data = self.unzip_waveform_data(waveform_data, 0,
                                                                     self.scan_properties['n_width'] - 1,
                                                                     index,
                                                                     self.scan_properties['rf_length'])
                        waveform_data = np.array(waveform_data)
                        waveform_data = np.reshape(waveform_data,
                                                   (1, self.scan_properties['n_width'], self.scan_properties['rf_length']))
                        waveforms.append(waveform_data)
        if len(waveforms) > 0:
            waveforms = np.vstack(waveforms)
            self._data['waveform'].append(waveforms)

    def read_waveform_data_pre240(self):
        """Reads the waveform datasets from UTWin files for versions prior to 2.40"""
        waveforms = []
        waveform_positions = UTWinCscanReader.find_blocks(self.data_file,
                                                          UTWinCscanReader.message_ids['WAVEFORM_pre240'])
        with open(self.data_file, "rb") as fidin:
            for pos in waveform_positions:
                fidin.seek(pos)
                rf_size = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['uint'])
                waveform_data = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'], rf_size)
                waveform_data = np.reshape(waveform_data,
                                           (self.scan_properties['n_height'], self.scan_properties['n_width'], -1))
                waveforms.append(waveform_data)
        if len(waveforms) > 0:
            waveforms = np.vstack(waveforms)
            self._data['waveform'].append(waveforms)

    def import_waveform_data(self):
        """Imports the waveform datasets into HDF5 files"""
        if len(self._data['waveform']) == 0:
            self.read_waveform_data()
        for dataset_idx in range(len(self._data['waveform'])):
            dataset = self._data['waveform'][dataset_idx]
            if dataset.size > 0:
                output_basename, ext = os.path.splitext(self.data_file)
                output_fname = os.path.join(pathfinder.data_path(),
                                            os.path.basename(output_basename) + "_waveformdata" + str(dataset_idx) + ext)
                save_data(output_fname, dataset)

    def read_amplitude_data(self):
        """Reads the amplitude datasets in the UTWin data file"""
        amplitude_positions = UTWinCscanReader.find_blocks(self.data_file, UTWinCscanReader.message_ids['UTSAVE_UTCD2'])
        with open(self.data_file, "rb") as fidin:
            for pos in amplitude_positions:
                fidin.seek(pos)
                gate = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['ushort'])
                nsize = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['int'])
                amp_data = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['short'], nsize)
                self._data['amplitude'].append(np.reshape(amp_data,
                                                          (self.scan_properties['n_height'],
                                                           self.scan_properties['n_width'])))

    def import_amplitude_data(self):
        """Imports the amplitude datasets as HDF5 files"""
        if len(self._data['amplitude']) == 0:
            self.read_amplitude_data()
        for dataset_idx in range(len(self._data['amplitude'])):
            dataset = self._data['amplitude'][dataset_idx]
            if dataset.size > 0:
                output_basename, ext = os.path.splitext(self.data_file)
                output_fname = os.path.join(pathfinder.data_path(),
                                            os.path.basename(output_basename) + "_ampdata" + str(dataset_idx) + ext)
                save_data(output_fname, dataset)

    def read_tof_data(self):
        """Reads the Time Of Flight (TOF) datasets from the UTWin data file"""
        tof_positions = UTWinCscanReader.find_blocks(self.data_file, UTWinCscanReader.message_ids['UTSAVE_UTCD1'])
        with open(self.data_file, "rb") as fidin:
            for pos in tof_positions:
                fidin.seek(pos)
                gate = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['ushort'])
                tof_start = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['float'])
                nsize = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['int'])
                tof_data = UTWinCscanReader.read_field(fidin, UTWinCscanReader.field_sizes['ushort'], nsize)
                tof_data = np.reshape(tof_data,
                                      (self.scan_properties['n_height'], self.scan_properties['n_width'])) * \
                           self.scan_properties['tof_resolution']
                self._data['tof'].append(tof_data)

    def import_tof_data(self):
        """Converts the TOF datasets to HDF5"""
        if len(self._data['tof']) == 0:
            self.read_tof_data()
        for dataset_idx in range(len(self._data['tof'])):
            dataset = self._data['tof'][dataset_idx]
            if dataset.size > 0:
                output_basename, ext = os.path.splitext(self.data_file)
                output_fname = os.path.join(pathfinder.data_path(),
                                            os.path.basename(output_basename) + "_tofdata" + str(dataset_idx) + ext)
                save_data(output_fname, dataset)

    def unzip_waveform_data(self, compressed_waveform_data, start_pos, stop_pos, index, wave_size):
        """Reverses run-length encoding compression on specified dataset."""
        uncompressed_data = [0 for el in range(self.scan_properties['n_width']*self.scan_properties['rf_length'])]
        dk = int(self.compression_properties['compression_ratio'])
        i = 0
        if dk <= 0 or self.compression_properties['compression_method'] == 0:
            dk = 1
        if self.compression_properties['is_threshold_compressed'] and\
                        (stop_pos - start_pos + 1) == self.scan_properties['n_width']:
            line_size = wave_size
            uncompressed_data = self.unzip_threshold_data(compressed_waveform_data, line_size)
        for n in range(start_pos, stop_pos+1):
            j = 0
            m = 0
            u1 = 0
            u2 = 0
            p = n * self.scan_properties['rf_length']
            d = n * self.compression_properties['compressed_rf_length']
            for i in range(dk, self.scan_properties['rf_length'], dk):
                if self.compression_properties['is_8bit_data']:
                    if j % 2 == 1:
                        z = compressed_waveform_data[d + m]
                        u1 = z & 0x00ff
                        u2 = (z & 0xff00) >> 8
                        u1 = u1 << self.compression_properties['compression_bit']
                        u2 = u2 << self.compression_properties['compression_bit']
                        for k in range(i - dk, i):
                            uncompressed_data[p + k] = u1
                            uncompressed_data[p + k - dk] = u2
                        m += 1
                    j += 1
                else:
                    u1 = compressed_waveform_data[d + m]
                    for k in range(i - dk, i):
                        uncompressed_data[p + k] = u1
                    m += 1
            while i < self.scan_properties['rf_length']:
                uncompressed_data[p + i] = u1
                i += 1
        return uncompressed_data

    def unzip_threshold_data(self, compressed_waveform_data, line_size):
        """Uncompresses data with a compressed threshold"""
        if self.compression_properties['is_8bit_data']:
            return self.unzip_8bit_threshold_data(compressed_waveform_data, line_size)
        else:
            return self.unzip_16bit_threshold_data(compressed_waveform_data, line_size)

    def unzip_8bit_threshold_data(self, compressed_waveform_data, line_size):
        """Uncompresses 8-Bit data with a compressed threshold"""
        uncompressed_data = [0 for el in range(self.scan_properties['n_width']*self.scan_properties['rf_length'])]
        bzip = False
        i = 0
        if line_size > 0:
            for j in range(0, line_size):
                z = compressed_waveform_data[j]
                for k in range(0, 2):
                    if k == 1:
                        a = z & 0x00ff
                    else:
                        a = (z & 0xff00) >> 8
                    if a == 0:
                        bzip = True
                    if a == 1:
                        if i % 2 == 0:
                            uncompressed_data[i / 2] = uncompressed_data[i / 2] & 0x00ff
                        else:
                            uncompressed_data[i / 2] = uncompressed_data[i / 2] & 0xff00
                        i += 1
                    elif a > 1 and bzip:
                        bzip = False
                        for _z in range(0, a):
                            if i % 2 == 0:
                                uncompressed_data[i / 2] = uncompressed_data[i / 2] & 0x00ff
                            else:
                                uncompressed_data[i / 2] = uncompressed_data[i / 2] & 0xff00
                                i += 1
                    elif not bzip:
                        if i % 2 == 0:
                            uncompressed_data[i / 2] = uncompressed_data[i / 2] & 0x00ff
                            u = a << 8
                            uncompressed_data[i / 2] = uncompressed_data[i / 2] | (u & 0xff00)
                        else:
                            uncompressed_data[i / 2] = uncompressed_data[i / 2] & 0xff00
                            uncompressed_data[i / 2] = uncompressed_data[i / 2] | (a & 0x00ff)
                        i += 1
                if i >= int(self.scan_properties['n_width'] * self.compression_properties['compressed_rf_length'] * 2):
                    #i = self.scan_properties['n_width'] * self.compression_properties['compressed_rf_length'] * 2
                    break
        return uncompressed_data

    def unzip_16bit_threshold_data(self, compressed_waveform_data, line_size):
        """Uncompresses 16-Bit data with a compressed threshold"""
        uncompressed_data = [0 for el in range(self.scan_properties['n_width']*self.scan_properties['rf_length'])]
        bzip = False
        i = 0
        if line_size > 0:
            for j in range(0, line_size):
                a = compressed_waveform_data[j]
                if a == 0:
                    bzip = True
                if a == 1:
                    uncompressed_data[i] = 0
                    i += 1
                elif a > 1 and bzip:
                    bzip = False
                    for _z in range(0, a):
                        uncompressed_data[i] = 0
                        i += 1
                elif not bzip:
                    uncompressed_data[i] = a
                    i += 1
                if i >= self.scan_properties['n_width'] * self.compression_properties['compressed_rf_length']:
                    #i = self.scan_properties['n_width'] * self.compression_properties['compressed_rf_length']
                    break
        return uncompressed_data

class WinspectReader(object):
    """Handles reading Winspect 6, 7 data files. Currently only unidirectional scans are supported.
    """

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
        datasets = self.get_winspect_data()
        amp_output_counter = 0
        waveform_output_counter = 0
        for dataset in datasets:
            if "amplitude" in dataset.data_type:
                output_fname = os.path.join(pathfinder.data_path(), os.path.basename(output_basename) + "_ampdata" +
                                                                    str(amp_output_counter) + ext)
                amp_output_counter += 1
            elif "waveform" in dataset.data_type:
                output_fname = os.path.join(pathfinder.data_path(), os.path.basename(output_basename) + "_waveformdata"
                                                                    + str(waveform_output_counter) + ext)
                waveform_output_counter += 1
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
