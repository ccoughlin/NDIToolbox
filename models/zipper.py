"""zipper.py - convenience classes for ZIP archives

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import zipfile

class UnZipper(object):
    """Handles unzipping ZIP archive files"""

    def __init__(self, zip_file, password=None):
        self.file = zip_file
        self.password = password
        if zipfile.is_zipfile(zip_file):
            self.zip = zipfile.ZipFile(self.file)
            self.zip.setpassword(self.password)
        else:
            raise TypeError("Specified file is not a valid ZIP archive.")

    def list_contents(self):
        """Returns a list of the archive members"""
        return self.zip.namelist()

    def is_ok(self):
        """Checks files in the ZIP archive and returns
        True if the archive appears valid, False if a
        bad file was found."""
        if self.zip.testzip() is None:
            return True
        return False

    def extractall(self, output_path):
        """Extracts the contents of the ZIP archive
        to the specified path."""
        self.zip.extractall(output_path)

    def extract(self, file_name, output_path):
        """Extracts the file file_name to the
        specified path."""
        self.zip.extract(file_name, path=output_path)

    def read(self, file_name):
        """Returns the bytes of the specified file from
        the ZIP archive."""
        return self.zip.read(file_name)