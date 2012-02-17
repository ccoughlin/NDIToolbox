"""test_zipper.py - tests the zipper module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import unittest
import filecmp
import os
import os.path
import shutil
import zipfile
from models import zipper

class TestUnzipper(unittest.TestCase):
    """Tests the Unzipper class"""

    def setUp(self):
        self.file_folder = os.path.join(os.path.dirname(__file__), 'support_files')
        self.destination_folder = os.path.join(os.path.dirname(__file__), 'temp_files')
        self.zip_file_path = os.path.join(self.file_folder, 'test.zip')
        self.generate_zip()

    def generate_file_list(self):
        """Returns a list of the files to be archived"""
        files_to_zip = []
        for root, dirs, files in os.walk(self.file_folder):
            for fname in files:
                basename, ext = os.path.splitext(fname)
                if ext.lower() in ('.png', '.jpg'):
                    file_name = os.path.join(root, fname)
                    files_to_zip.append(file_name)
        return files_to_zip

    def generate_zip(self):
        """Creates a small ZIP archive for testing"""
        with zipfile.ZipFile(self.zip_file_path, 'w') as zip_output:
            for file_name in self.generate_file_list():
                zip_output.write(file_name)

    def get_zip(self):
        """Returns a file object handle to a small
        ZIP archive"""
        return open(self.zip_file_path, 'r')

    def test_init_path(self):
        """Verify instantiation with a path to a ZIP file"""
        unzipper = zipper.UnZipper(zip_file=self.zip_file_path, password="123")
        self.assertEqual(unzipper.file, self.zip_file_path)
        self.assertEqual(unzipper.password, "123")

    def test_init_file(self):
        """Verify instantiation with a file-like object handle
        to a ZIP file"""
        a_zip = self.get_zip()
        unzipper = zipper.UnZipper(zip_file=a_zip, password="123")
        self.assertEqual(unzipper.file, a_zip)
        self.assertEqual(unzipper.password, "123")
        if not a_zip.closed:
            a_zip.close()

    def test_init_bad_zip(self):
        """Verify instantiation raises a TypeError if the specified
        file is not a ZIP archive"""
        with self.assertRaises(TypeError):
            unzipper = zipper.UnZipper(zip_file=__file__)

    def test_list_contents(self):
        """Verify listing of ZIP contents"""
        unzipper = zipper.UnZipper(zip_file=self.zip_file_path)
        with zipfile.ZipFile(self.zip_file_path, 'r') as a_zip:
            self.assertListEqual(a_zip.namelist(), unzipper.list_contents())

    def test_is_ok(self):
        """Verify UnZipper returns True if files appear ok"""
        unzipper = zipper.UnZipper(zip_file=self.zip_file_path)
        self.assertTrue(unzipper.is_ok())

    def test_extractall(self):
        """Verify extraction of all the files in the ZIP"""
        unzipper = zipper.UnZipper(zip_file=self.zip_file_path)
        original_files = {os.path.basename(orig_file):orig_file for orig_file in
                          self.generate_file_list()}
        unzipper.extractall(self.destination_folder)
        for root, dirs, files in os.walk(self.destination_folder):
            for fname in files:
                basename, ext = os.path.splitext(fname)
                if ext.lower() in ('.png', '.jpg'):
                    file_name = os.path.join(root, fname)
                    self.assertTrue(filecmp.cmp(file_name, original_files[fname]))

    def test_extract(self):
        """Verify extraction of a single file"""
        unzipper = zipper.UnZipper(zip_file=self.zip_file_path)
        original_files = {os.path.basename(orig_file):orig_file for orig_file in
                          self.generate_file_list()}
        for each in unzipper.list_contents():
            unzipper.extract(each, self.destination_folder)
        for root, dirs, files in os.walk(self.destination_folder):
            for fname in files:
                basename, ext = os.path.splitext(fname)
                if ext.lower() in ('.png', '.jpg'):
                    file_name = os.path.join(root, fname)
                    self.assertTrue(filecmp.cmp(file_name, original_files[fname]))

    def test_read(self):
        """Verify reading a single file from the ZIP"""
        unzipper = zipper.UnZipper(zip_file=self.zip_file_path)
        original_files = {os.path.basename(orig_file):orig_file for orig_file in
                          self.generate_file_list()}
        for root, dirs, files in os.walk(self.file_folder):
            for fname in files:
                basename, ext = os.path.splitext(fname)
                if ext.lower() in ('.png', '.jpg'):
                    file_name = os.path.join(root, fname)
                    # Files are stored with relative paths
                    # in ZIPs, remove the '/' or 'drive:\'
                    # from root
                    rel_path = file_name.split(os.sep, 1)[-1]
                    with open(file_name, "rb") as original_file:
                        self.assertEqual(original_file.read(),
                            unzipper.read(rel_path))

    def tearDown(self):
        if os.path.exists(self.zip_file_path):
            os.remove(self.zip_file_path)
        if os.path.exists(self.destination_folder):
            shutil.rmtree(self.destination_folder)

if __name__ == "__main__":
    unittest.main()