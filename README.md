NDIToolbox - Signal Processing For Nondestructive Inspection Data
=================================================================

* Author:	Chris Coughlin (TRI/Austin, Inc.) <ccoughlin@tri-austin.com>
* Website:  <http://www.nditoolbox.com>

NDIToolbox is an extensible signal and image processing application written in Python designed to assist with the analysis of complex NDI data.

Features
--------
* Plot and preview NDE data files - A, B, and C scan presentations
* Some basic data manipulation routines (more added all the time)
* Uses the open source Hierarchical Data Format (<http://www.hdfgroup.org/HDF5/>) for data files - access your data from any number of other tools including Java, MATLAB, IDL, and C/C++
* Generate thumbnails of data files - makes it easier to browse through reams of data
* Extensible with plugins - write your own NDI analysis scripts without worrying about creating a user interface
* Import data from commercial NDE systems
* Import basic DICOM / DICONDE (<http://www.astm.org/COMMIT/DICONDE_Information.htm>) data files
* Import images as data (PNG, JPEG, TIFF, BMP, EPS, etc.); export plots as PNG, EPS, PDF, etc.
* Import delimited ASCII data files; export data from other formats to ASCII
* Probability Of Detection (POD) Toolkit - create, edit and run POD (<http://www.asnt.org/publications/materialseval/basics/jan98basics/jan98basics.htm>) models of NDI measurements

NDIToolbox is available as both a standard Python application and a precompiled Windows binary.  Generally we recommend you run the Python version, but the Windows EXE is a good choice if you just want to test NDIToolbox and/or don't want to install Python and other packages.

System Requirements
-------------------
NDIToolbox should run on fairly modest systems e.g. 2.93GHz Core 2 Duo, 2GB RAM, 100MB free disk space.  If you expect to work with large (500MB+) data files, you should have at least 4GB of RAM, preferably 8GB or more if you expect you'll use the MegaPlot presentation.  

Requirements - Python Application
---------------------------------
NDIToolbox is a Python (<http://www.python.org>) application and should run on most operating systems that support Python 2.7 and has been tested on Windows XP, Windows 7, and various flavors of 32 and 64-bit Linux.  In addition to Python NDIToolbox has a few additional dependencies:

* wxPython (<http://www.wxpython.org>)
* NumPy and SciPy (<http://www.scipy.org>)
* matplotlib (<http://matplotlib.sf.net>)
* pydicom (<http://code.google.com/p/pydicom>)
* HDF5 for Python (<http://code.google.com/p/h5py/>)
* Python Imaging Library (<http://www.pythonware.com/products/pil/>) (only necessary if you need to import images)
* ReportLab (<http://www.reportlab.com/>) and PyPdf (<http://pybrary.net/pyPdf/>) (only necessary if you need to generate PDFs)

Requirements - Standalone Windows Binary
----------------------------------------
NDIToolbox is also available as a standalone windows binary that doesn't require Python to be installed.

Installation - Python Application
---------------------------------
Once you have Python and the additional dependencies installed, download NDIToolbox and run the nditoolbox.py file in the root folder.  On first startup NDIToolbox will create a new folder in your home folder for storing local files.  By default this folder is called nditoolbox and is placed under your $HOME folder (e.g. c:\users\chris in Windows 7/8 or /home/chris under Linux), but you can choose an alternate destination if desired.

To uninstall, delete the NDIToolbox folder.  For complete removal, you can also delete the folder NDIToolbox created to store local files.

Installation - Standalone Windows Binary
----------------------------------------
For a standard installation, download the NDIToolbox Installer.exe package from the Downloads page and run as usual.  If you'd prefer a portable version you can run off a flash drive, download the nditoolbox_windows_binary.zip file from the Downloads page and extract to a folder of your choosing.  Run nditoolbox.exe from this folder to start NDIToolbox.  On first startup NDIToolbox will create a new folder in your home folder for storing local files.  By default this folder is called nditoolbox and is placed under your $HOME folder (e.g. c:\users\chris in Windows 7/8 or /home/chris under Linux), but you can choose an alternate destination if desired.

To uninstall the standard installation, use Control Panel's Add or Remove Programs (Windows XP) or Uninstall a program (Windows 7).  To uninstall the portable version, delete the NDIToolbox folder.  In either case for complete removal you can also delete the folder NDIToolbox created to store local files.

Acknowledgements
----------------------
* Axialis (<http://www.axialis.com/iconworkshop/>)
* Computational Tools (<http://www.computationaltools.com/>)
* pydicom (<http://code.google.com/p/pydicom>)
* HDF5 for Python (<http://code.google.com/p/h5py/>)
* ASTM Committee E07 On Nondestructive Testing (<http://www.astm.org/COMMIT/COMMITTEE/E07.htm>)