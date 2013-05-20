"""test_dataio.py - tests the dataio module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import unittest
from models import dataio
from controllers import pathfinder
from utils.skiptest import skipIfModuleNotInstalled
import h5py
import numpy as np
import numpy.testing
import scipy.misc
import os
import random


class TestDataIO(unittest.TestCase):
    """Tests Data IO functions"""

    def setUp(self):
        self.sample_data = np.array(self.random_data())
        self.sample_data_basename = "sample.dat"
        self.sample_data_file = os.path.join(os.path.dirname(__file__),
                                             self.sample_data_basename)
        with h5py.File(self.sample_data_file, 'w') as fidout:
            fidout.create_dataset(self.sample_data_basename, data=self.sample_data)

    def random_data(self):
        """Returns a list of random data"""
        return [random.uniform(-100, 100) for i in range(25)]

    def test_save_data(self):
        """Verify save_data function saves NumPy array to disk"""
        sample_filename = "test_savedata.dat"
        sample_path = os.path.join(os.path.dirname(__file__), sample_filename)
        dataio.save_data(sample_path, self.sample_data)
        self.assertTrue(os.path.exists(sample_path + ".hdf5"))
        with h5py.File(sample_path + ".hdf5", "r") as fidin:
            froot, ext = os.path.splitext(os.path.basename(sample_filename))
            for key in fidin.keys():
                if key.startswith(froot):
                    read_data = fidin[key][...]
                    self.assertTrue(np.array_equal(self.sample_data, read_data))
        if os.path.exists(sample_path + ".hdf5"):
            os.remove(sample_path + ".hdf5")

    def test_get_data(self):
        """Verify get_data function returns a NumPy array"""
        read_data = dataio.get_data(self.sample_data_file)
        self.assertTrue(np.array_equal(self.sample_data, read_data))

    def test_get_data_slice(self):
        """Verify get_data function returns a slice if specified"""
        slice_idx = np.s_[5:15]
        read_hyperslab = dataio.get_data(self.sample_data_file, slice_idx)
        self.assertTrue(np.array_equal(self.sample_data[slice_idx], read_hyperslab))

    def test_get_txt_data(self):
        """Verify retrieval of ASCII delimited data"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files',
                                        '1.25 from hole Single Column.asc')
        assert(os.path.exists(sample_data_file))
        import_params = {'delimiter': None}
        expected_data = np.loadtxt(sample_data_file, delimiter=import_params['delimiter'])
        retrieved_data = dataio.get_txt_data(sample_data_file, **import_params)
        self.assertTrue(np.array_equal(expected_data, retrieved_data))

    def test_import_txt(self):
        """Verify import of ASCII delimited data files"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files',
                                        '1.25 from hole Single Column.asc')
        assert(os.path.exists(sample_data_file))
        import_params = {'delimiter': None}
        expected_data = np.loadtxt(sample_data_file, delimiter=import_params['delimiter'])
        dataio.import_txt(sample_data_file, **import_params)
        dest_file = os.path.join(pathfinder.data_path(),
                                 os.path.basename(sample_data_file) + ".hdf5")
        self.assertTrue(os.path.exists(dest_file))
        with h5py.File(dest_file, "r") as fidin:
            root, ext = os.path.splitext(os.path.basename(dest_file))
            for key in fidin.keys():
                if key.startswith(root):
                    read_data = fidin[key][...]
                    self.assertTrue(np.array_equal(expected_data, read_data))
        try:
            if os.path.exists(dest_file):
                os.remove(dest_file)
        except WindowsError: # file in use
            pass

    def test_export_txt(self):
        """Verify export of data to delimited ASCII"""
        # Use integer data to avoid the floating point conversion to/from files
        sample_data = self.sample_data.astype(np.int64)
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files',
                                        'sample.hdf5')
        dest_file = os.path.join(os.path.dirname(__file__), 'support_files',
                                 'sample.txt')
        with h5py.File(sample_data_file, "w") as fidout:
            fidout.create_dataset(os.path.basename(sample_data_file), data=sample_data)
            export_params = {'delimiter': ','}
            dataio.export_txt(dest_file, sample_data_file, **export_params)
            retrieved_data = np.genfromtxt(dest_file, delimiter=export_params['delimiter'])
            self.assertTrue(np.array_equal(sample_data, retrieved_data))
        try:
            if os.path.exists(sample_data_file):
                os.remove(sample_data_file)
            if os.path.exists(dest_file):
                os.remove(dest_file)
        except WindowsError: # file in use
            pass

    def test_export3D_txt(self):
        """Verify export of 3D data to delimited ASCII"""
        x_size = 5
        y_size = 4
        z_size = 6
        sample_data = np.empty((y_size, x_size, z_size))
        for xidx in range(x_size):
            for yidx in range(y_size):
                for zidx in range(z_size):
                    sample_data[yidx, xidx, zidx] = int(random.uniform(-100, 100))
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'sample3d.hdf5')
        dest_file = os.path.join(os.path.dirname(__file__), 'support_files', 'sample3d.txt')
        with h5py.File(sample_data_file, "w") as fidout:
            fidout.create_dataset(os.path.basename(sample_data_file), data=sample_data)
            export_params = {'delimiter': ','}
            dataio.export_txt(dest_file, sample_data_file, **export_params)
            retrieved_data = np.empty(sample_data.shape)
            with open(dest_file, "rb") as fidin:
                zidx = 0
                for line in fidin:
                    if not line.startswith('#'):
                        x, y, z = line.split(export_params['delimiter'])
                        x = int(x)
                        y = int(y)
                        z = float(z.strip())
                        retrieved_data[y, x, zidx] = z
                        zidx += 1
                        if zidx > sample_data.shape[2]-1:
                            zidx = 0
            self.assertTrue(np.array_equal(sample_data, retrieved_data))
        try:
            if os.path.exists(sample_data_file):
                os.remove(sample_data_file)
            if os.path.exists(dest_file):
                os.remove(dest_file)
        except WindowsError: # file in use
            pass

    @skipIfModuleNotInstalled("dicom")
    def test_get_dicom_data(self):
        """Verify retrieval of DICOM / DICONDE data"""
        import dicom
        diconde_folder = os.path.join(os.path.dirname(__file__), 'support_files')
        for root, dirs, files in os.walk(diconde_folder):
            for fname in files:
                dicom_data_file = os.path.join(root, fname)
                basename, ext = os.path.splitext(dicom_data_file)
                # Simple check to ensure we're looking at DICOM files
                if ext.lower() == '.dcm':
                    dicom_data = dicom.read_file(dicom_data_file)
                    dicom_arr = dicom_data.pixel_array
                    retrieved_data = dataio.get_dicom_data(dicom_data_file)
                    self.assertTrue(np.array_equal(dicom_arr, retrieved_data))

    @skipIfModuleNotInstalled("dicom")
    def test_import_dicom(self):
        """Verify import of DICOM / DICONDE data"""
        # Load the ASTM DICONDE example files,
        # save, then ensure the resulting arrays
        # are identical
        import dicom

        diconde_folder = os.path.join(os.path.dirname(__file__), 'support_files')
        for root, dirs, files in os.walk(diconde_folder):
            for fname in files:
                dicom_data_file = os.path.join(root, fname)
                basename, ext = os.path.splitext(dicom_data_file)
                # Simple check to ensure we're looking at DICOM files
                if ext.lower() == '.dcm':
                    dicom_data = dicom.read_file(dicom_data_file)
                    dicom_arr = dicom_data.pixel_array
                    dataio.import_dicom(dicom_data_file)
                    dest_file = os.path.join(pathfinder.data_path(),
                                             os.path.basename(dicom_data_file) + ".hdf5")
                    self.assertTrue(os.path.exists(dest_file))
                    with h5py.File(dest_file, "r") as fidin:
                        froot, ext = os.path.splitext(os.path.basename(dest_file))
                        for key in fidin.keys():
                            if key.startswith(froot):
                                read_data = fidin[key][...]
                                self.assertTrue(np.array_equal(dicom_arr, read_data))
                    try:
                        if os.path.exists(dest_file):
                            os.remove(dest_file)
                    except WindowsError: # File in use
                        pass

    @skipIfModuleNotInstalled("Image", "PIL")
    def test_get_img_data(self):
        """Verify retrieval of bitmap data"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files',
                                        'austin_sky320x240.jpg')
        assert(os.path.exists(sample_data_file))
        expected_data = scipy.misc.imread(sample_data_file, flatten=True)
        retrieved_data = dataio.get_img_data(sample_data_file, flatten=True)
        self.assertTrue(np.array_equal(expected_data, retrieved_data))

    @skipIfModuleNotInstalled("Image", "PIL")
    def test_import_img(self):
        """Verify import of images"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files',
                                        'austin_sky320x240.jpg')
        assert(os.path.exists(sample_data_file))
        expected_data = scipy.misc.imread(sample_data_file, flatten=True)
        dataio.import_img(sample_data_file, flatten=True)
        dest_file = os.path.join(pathfinder.data_path(),
                                 os.path.basename(sample_data_file) + ".hdf5")
        self.assertTrue(os.path.exists(dest_file))
        with h5py.File(dest_file, "r") as fidin:
            root, ext = os.path.splitext(os.path.basename(dest_file))
            for key in fidin.keys():
                if key.startswith(root):
                    read_data = fidin[key][...]
                    self.assertTrue(np.array_equal(expected_data, read_data))
        try:
            if os.path.exists(dest_file):
                os.remove(dest_file)
        except WindowsError: # file in use
            pass

    def test_get_utwin_tof_data(self):
        """Verify retrieval of UTWin Time Of Flight data through convenience function"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData.csc')
        tof_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData_tofdata.npy')
        tof_resolution = 0.01
        assert(os.path.exists(tof_data_file))
        expected_tof_data = np.load(tof_data_file) * tof_resolution
        returned_tof_data = dataio.get_utwin_tof_data(sample_data_file)[0]
        numpy.testing.assert_array_almost_equal(expected_tof_data, returned_tof_data, decimal=3)

    def test_import_utwin_tof(self):
        """Verify import of UTWin Time Of Flight data through convenience function"""
        tof_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData_tofdata.npy')
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData.csc')
        tof_resolution = 0.01
        expected_tof_data = np.load(tof_data_file) * tof_resolution
        root, ext = os.path.splitext(os.path.basename(sample_data_file))
        dest_file = os.path.join(pathfinder.data_path(),
                                 os.path.basename(root) + "_tofdata0.csc.hdf5")
        dataio.import_utwin_tof(sample_data_file)
        self.assertTrue(os.path.exists(dest_file))
        with h5py.File(dest_file, "r") as fidin:
            root, ext = os.path.splitext(os.path.basename(dest_file))
            for key in fidin.keys():
                if key.startswith(root):
                    read_data = fidin[key][...]
                    numpy.testing.assert_array_almost_equal(expected_tof_data, read_data, decimal=3)
        try:
            if os.path.exists(dest_file):
                os.remove(dest_file)
        except WindowsError: # file in use
            pass

    def test_get_utwin_amp_data(self):
        """Verify retrieval of UTWin amplitude data through convenience function"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData.csc')
        amp_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData_ampdata.npy')
        assert(os.path.exists(amp_data_file))
        expected_tof_data = np.load(amp_data_file)
        self.assertTrue(np.array_equal(expected_tof_data, dataio.get_utwin_amp_data(sample_data_file)[0]))

    def test_import_utwin_amp(self):
        """Verify import of UTWin amplitude data through convenience function"""
        amp_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData_ampdata.npy')
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData.csc')
        expected_amp_data = np.load(amp_data_file)
        root, ext = os.path.splitext(os.path.basename(sample_data_file))
        dest_file = os.path.join(pathfinder.data_path(),
                                 os.path.basename(root) + "_ampdata0.csc.hdf5")
        dataio.import_utwin_amp(sample_data_file)
        self.assertTrue(os.path.exists(dest_file))
        with h5py.File(dest_file, "r") as fidin:
            root, ext = os.path.splitext(os.path.basename(dest_file))
            for key in fidin.keys():
                if key.startswith(root):
                    read_data = fidin[key][...]
                    self.assertTrue(np.array_equal(expected_amp_data, read_data))
        try:
            if os.path.exists(dest_file):
                os.remove(dest_file)
        except WindowsError: # file in use
            pass

    def test_get_utwin_data(self):
        """Verify returning UTWin data"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData.csc')
        sample_reader = dataio.UTWinCScanDataFile(sample_data_file)
        sample_reader.read_data()
        expected_data = sample_reader.data
        returned_data = dataio.get_utwin_data(sample_data_file)
        for datatype in expected_data:
            self.assertTrue(np.array_equal(expected_data[datatype], returned_data[datatype]))

    def test_get_winspect_data(self):
        """Verify retrieval of Winspect data through convenience function"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'sample_data.sdt')
        assert(os.path.exists(sample_data_file))
        scan_reader = dataio.WinspectReader(sample_data_file)
        expected_data_list = scan_reader.get_winspect_data()
        retrieved_data_list = dataio.get_winspect_data(sample_data_file)
        self.assertEqual(len(expected_data_list), len(retrieved_data_list))
        for data_array_idx in range(len(expected_data_list)):
            self.assertTrue(np.array_equal(expected_data_list[data_array_idx].data, retrieved_data_list[data_array_idx].data))

    def test_import_winspect(self):
        """Verify import of Winspect data through convenience function"""
        sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'sample_data.sdt')
        assert(os.path.exists(sample_data_file))
        output_basename, ext = os.path.splitext(sample_data_file)
        amp_dest_file = os.path.join(pathfinder.data_path(),
                                     os.path.basename(output_basename) + "_ampdata0" + ext + ".hdf5")
        waveform_dest_file = os.path.join(pathfinder.data_path(),
                                          os.path.basename(output_basename) + "_waveformdata0" + ext + ".hdf5")
        dataio.import_winspect(sample_data_file)
        expected_data_list = dataio.get_winspect_data(sample_data_file)
        for dataset in expected_data_list:
            if "amplitude" in dataset.data_type:
                dest_file = amp_dest_file
            elif "waveform" in dataset.data_type:
                dest_file = waveform_dest_file
            with h5py.File(dest_file, "r") as fidin:
                root, ext = os.path.splitext(os.path.basename(dest_file))
                for key in fidin.keys():
                    if key.startswith(root):
                        read_data = fidin[key][...]
                        self.assertTrue(np.array_equal(dataset.data, read_data))
            try:
                if os.path.exists(dest_file):
                    os.remove(dest_file)
            except WindowsError: # file in use
                pass

    def tearDown(self):
        if os.path.exists(self.sample_data_file + ".hdf5"):
            os.remove(self.sample_data_file + ".hdf5")
        if os.path.exists(self.sample_data_file):
            os.remove(self.sample_data_file)


class TestUTWinCScanReader(unittest.TestCase):
    """Tests the UTWinCScanReader class"""

    def setUp(self):
        self.sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData.csc')
        assert(os.path.exists(self.sample_data_file))
        self.cscan_reader = dataio.UTWinCscanReader()

    def test_basicfile_parameters(self):
        """Verify the basic parameters of the CSC file format are correct"""
        self.assertEqual(self.cscan_reader.header_string_length, 15)
        expected_message_ids = {'CSCAN_DATA': 2300,
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
        self.assertDictEqual(expected_message_ids, self.cscan_reader.message_ids)

    def test_is_cscanfile(self):
        """Verify reader correctly identifies CSC files"""
        self.assertTrue(self.cscan_reader.is_cscanfile(self.sample_data_file))

    def test_msg_info(self):
        """Verify reader correctly returns message ID and length"""
        with open(self.sample_data_file, "rb") as fidin:
            fidin.seek(self.cscan_reader.header_string_length)
            first_message = (100, 14)
            self.assertTupleEqual(first_message, self.cscan_reader.msg_info(fidin))

    def test_find_message(self):
        """Verify find_message returns the expected file positions"""
        expected_file_positions = ((2014, 38037),
                                   (2011, 38059),
                                   (2010, 38003),
                                   (2012, 422075),
                                   (2010, 38003),
                                   (2010, 38003))
        for message_id, expected_pos in expected_file_positions:
            self.assertEqual(self.cscan_reader.find_message(self.sample_data_file, message_id), expected_pos)

    def test_find_blocks(self):
        """Verify find_blocks returns the file positions for the specified message ID"""
        # Search for UTSave_UTAD0 (Message ID 950) - contains A/D settings for each channel
        expected_filed_positions = [173, 920, 1667, 2414, 3161, 3908, 4655, 5402]
        self.assertListEqual(expected_filed_positions, self.cscan_reader.find_blocks(self.sample_data_file, 950))

    def test_read_field(self):
        """Verify read_field correctly parses the specified message block"""
        start_pos = self.cscan_reader.find_message(self.sample_data_file, 950)
        self.assertTrue(start_pos != -1)
        with open(self.sample_data_file, "rb") as fidin:
            fidin.seek(start_pos)
            # Read a sample of A/D settings for the first channel
            expected_ad_delay = np.fromfile(fidin, self.cscan_reader.field_sizes['float'], 1)[0]
            expected_ad_width = np.fromfile(fidin, self.cscan_reader.field_sizes['float'], 1)[0]
            expected_ad_blanking_width = np.fromfile(fidin, self.cscan_reader.field_sizes['float'], 1)[0]
            expected_ad_gain = np.fromfile(fidin, self.cscan_reader.field_sizes['float'], 1)[0]
            expected_ad_offset = np.fromfile(fidin, self.cscan_reader.field_sizes['float'], 1)[0]
            expected_ad_trigger_level = np.fromfile(fidin, self.cscan_reader.field_sizes['float'], 1)[0]
            expected_ad_trigger_rate = np.fromfile(fidin, self.cscan_reader.field_sizes['float'], 1)[0]
        with open(self.sample_data_file, "rb") as fidin:
            fidin.seek(start_pos)
            ad_delay = self.cscan_reader.read_field(fidin, self.cscan_reader.field_sizes['float'])
            ad_width = self.cscan_reader.read_field(fidin, self.cscan_reader.field_sizes['float'])
            ad_blanking_width = self.cscan_reader.read_field(fidin, self.cscan_reader.field_sizes['float'])
            ad_gain = self.cscan_reader.read_field(fidin, self.cscan_reader.field_sizes['float'])
            ad_offset = self.cscan_reader.read_field(fidin, self.cscan_reader.field_sizes['float'])
            ad_trigger_level = self.cscan_reader.read_field(fidin, self.cscan_reader.field_sizes['float'])
            ad_trigger_rate = self.cscan_reader.read_field(fidin, self.cscan_reader.field_sizes['float'])
        self.assertAlmostEqual(expected_ad_delay, ad_delay)
        self.assertAlmostEqual(expected_ad_width, ad_width)
        self.assertAlmostEqual(expected_ad_blanking_width, ad_blanking_width)
        self.assertAlmostEqual(expected_ad_gain, ad_gain)
        self.assertAlmostEqual(expected_ad_offset, ad_offset)
        self.assertAlmostEqual(expected_ad_trigger_level, ad_trigger_level)
        self.assertAlmostEqual(expected_ad_trigger_rate, ad_trigger_rate)


class TestUTWinCScanDataFile(unittest.TestCase):
    """Tests the UTWinCScanDataFile class.

    Note:  the sample UTWin data files available to TRI as of May 2013 are export-controlled and can't be
    distributed, which in turn limits the tests that can be performed.  The UTWinCScanDataFile class has been
    tested against real inspection data, however without additional sample files you should consider the code
    experimental.  For more details, contact TRI.
    """

    def setUp(self):
        self.sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData.csc')
        self.cscan_datafile = dataio.UTWinCScanDataFile(self.sample_data_file)

    def test_get_scan_version(self):
        """Verify get_scan_version returns the correct scan version"""
        self.assertEqual(self.cscan_datafile.get_scan_version(), 117)

    def test_read_scan_properties(self):
        """Verify read_scan_properties correctly compiles required scan settings"""
        # Read a sample of the most important properties, verify read
        important_scan_properties = {'n_height':320,
                                     'n_width':600,
                                     'rf_length':2994,
                                     'channel_active':[1, 0, 0, 0, 0, 0, 0, 0]}
        for idx in important_scan_properties.keys():
            prop = important_scan_properties[idx]
            if not isinstance(prop, list):
                self.assertEqual(prop, self.cscan_datafile.scan_properties[idx])
            else:
                self.assertListEqual(prop, self.cscan_datafile.scan_properties[idx])

    def test_read_tof_data(self):
        """Verify read_tof_data correctly reads Time Of Flight data"""
        # Verify one TOF dataset
        tof_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData_tofdata.npy')
        tof_resolution = 0.01
        assert(os.path.exists(tof_data_file))
        expected_tof_data = np.load(tof_data_file) * tof_resolution
        self.cscan_datafile.read_tof_data()
        numpy.testing.assert_array_almost_equal(expected_tof_data, self.cscan_datafile.data['tof'][0], decimal=3)

    def test_read_amplitude_data(self):
        """Verify read_amplitude_data correctly reads amplitude data"""
        amp_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData_ampdata.npy')
        assert(os.path.exists(amp_data_file))
        expected_amp_data = np.load(amp_data_file)
        self.cscan_datafile.read_amplitude_data()
        self.assertTrue(np.array_equal(expected_amp_data, self.cscan_datafile.data['amplitude'][0]))

    def test_import_tof(self):
        """Verify import of Time Of Flight data"""
        tof_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData_tofdata.npy')
        tof_resolution = 0.01
        csc_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData')
        assert(os.path.exists(tof_data_file))
        expected_tof_data = np.load(tof_data_file) * tof_resolution
        dest_file = os.path.join(pathfinder.data_path(),
                                 os.path.basename(csc_data_file) + "_tofdata0.csc.hdf5")
        self.cscan_datafile.import_tof_data()
        self.assertTrue(os.path.exists(dest_file))
        with h5py.File(dest_file, "r") as fidin:
            root, ext = os.path.splitext(os.path.basename(dest_file))
            for key in fidin.keys():
                if key.startswith(root):
                    read_data = fidin[key][...]
                    numpy.testing.assert_array_almost_equal(expected_tof_data, read_data, decimal=3)
        try:
            if os.path.exists(dest_file):
                os.remove(dest_file)
        except WindowsError: # file in use
            pass

    def test_import_amp(self):
        """Verify import of amplitude data"""
        amp_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData_ampdata.npy')
        csc_data_file = os.path.join(os.path.dirname(__file__), 'support_files', 'CScanData')
        assert(os.path.exists(amp_data_file))
        expected_amp_data = np.load(amp_data_file)
        dest_file = os.path.join(pathfinder.data_path(),
                                 os.path.basename(csc_data_file) + "_ampdata0.csc.hdf5")
        self.cscan_datafile.import_amplitude_data()
        self.assertTrue(os.path.exists(dest_file))
        with h5py.File(dest_file, "r") as fidin:
            root, ext = os.path.splitext(os.path.basename(dest_file))
            for key in fidin.keys():
                if key.startswith(root):
                    read_data = fidin[key][...]
                    self.assertTrue(np.array_equal(expected_amp_data, read_data))
        try:
            if os.path.exists(dest_file):
                os.remove(dest_file)
        except WindowsError: # file in use
            pass


class TestWinspectReader(unittest.TestCase):
    """Tests the WinspectReader class."""

    def setUp(self):
        self.sample_data_file = os.path.join(os.path.dirname(__file__), 'support_files',
                                             'sample_data.sdt')
        assert(os.path.exists(self.sample_data_file))
        self.scan_reader = dataio.WinspectReader(self.sample_data_file)

    def test_find_numbers(self):
        """Verify find_numbers static method correctly pulls numbers from strings"""
        float_strings = {"0.000000 mm":0.0, "0.775995 Usec":0.775995}
        int_strings = {"35 18 0 22 3 112 ":[35, 18, 0, 22, 3, 112],
                       "Number of Sample Points          : 3500":3500}
        bad_strings = {"Ramshackle":[], "":[]}
        for string in float_strings:
            self.assertAlmostEqual(float_strings[string], self.scan_reader.find_numbers(string))

    def test_get_winspect_data(self):
        """Verify returning the list of arrays read from the data file"""
        data_reader = dataio.WinspectDataFile(self.sample_data_file)
        data_reader.read_data()
        expected_data_list = data_reader.datasets
        retrieved_data_list = self.scan_reader.get_winspect_data()
        self.assertEqual(len(expected_data_list), len(retrieved_data_list))
        for data_array_idx in range(len(expected_data_list)):
            self.assertTrue(np.array_equal(expected_data_list[data_array_idx].data, retrieved_data_list[data_array_idx].data))

    def test_import_winspect(self):
        """Verify importing datasets"""
        output_basename, ext = os.path.splitext(self.sample_data_file)
        amp_dest_file = os.path.join(pathfinder.data_path(),
                                 os.path.basename(output_basename) + "_ampdata0" + ext + ".hdf5")
        waveform_dest_file = os.path.join(pathfinder.data_path(),
                                          os.path.basename(output_basename) + "_waveformdata0" + ext + ".hdf5")
        self.scan_reader.import_winspect()
        data_reader = dataio.WinspectDataFile(self.sample_data_file)
        data_reader.read_data()
        expected_data_list = data_reader.datasets
        for dataset in expected_data_list:
            if "amplitude" in dataset.data_type:
                dest_file = amp_dest_file
            elif "waveform" in dataset.data_type:
                dest_file = waveform_dest_file
            with h5py.File(dest_file, "r") as fidin:
                root, ext = os.path.splitext(os.path.basename(dest_file))
                for key in fidin.keys():
                    if key.startswith(root):
                        read_data = fidin[key][...]
                        self.assertTrue(np.array_equal(dataset.data, read_data))
            try:
                if os.path.exists(dest_file):
                    os.remove(dest_file)
            except WindowsError: # file in use
                pass


if __name__ == "__main__":
    random.seed()
    unittest.main()