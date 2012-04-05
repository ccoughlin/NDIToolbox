NDIToolbox - Signal Processing For Nondestructive Inspection Data
=================================================================

* Author:	Chris Coughlin (TRI/Austin, Inc.) <ccoughlin@tri-austin.com>
* Website:  <http://www.nditoolbox.com>

NDIToolbox is an extensible signal and image processing application written in Python designed to assist with the analysis of complex NDI data.

Features
----------
* Plot and preview NDE data files
* Uses the open source Hierarchical Data Format (<http://www.hdfgroup.org/HDF5/>) for data files - access your data from any number of other tools including Java, MATLAB, IDL, and C/C++
* Generate thumbnails of data files - makes it easier to browse through reams of data
* Extensible with plugins - write your own NDI analysis scripts without worrying about creating a user interface
* Import basic DICOM / DICONDE (<http://www.astm.org/COMMIT/DICONDE_Information.htm>) data files
* Import and export delimited ASCII data files
* Probability Of Detection (POD) Toolkit - create, edit and run POD (<http://www.asnt.org/publications/materialseval/basics/jan98basics/jan98basics.htm>) models of NDI measurements

Requirements
----------------
NDIToolbox is a Python (<http://www.python.org>) application and should run on most operating systems that support Python 2.7 and has been tested on Windows XP, Windows 7, and various flavors of 32 and 64-bit Linux.  In addition to Python NDIToolbox has a few additional dependencies:

* wxPython (<http://www.wxpython.org>)
* NumPy and SciPy (<http://www.scipy.org>)
* matplotlib (<http://matplotlib.sf.net>)
* pydicom (<http://code.google.com/p/pydicom>)
* HDF5 for Python (<http://code.google.com/p/h5py/>)

Installation
-------------
In the future we might have a full-blown installation package available, but for now NDIToolbox is distributed as a simple Python application.  Once you have Python and the additional dependencies installed, download NDIToolbox and run the a7117.py file in the root folder.  On first startup NDIToolbox will create a new folder in your home folder for storing local files.

Acknowledgements
----------------------
* Axialis (<http://www.axialis.com/iconworkshop/>)
* Computational Tools (<http://www.computationaltools.com/>)
* pydicom (<http://code.google.com/p/pydicom>)
* HDF5 for Python (<http://code.google.com/p/h5py/>)
* ASTM Committee E07 On Nondestructive Testing (<http://www.astm.org/COMMIT/COMMITTEE/E07.htm>)