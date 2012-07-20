__author__ = 'Chris R. Coughlin'

from views import mainui
from models import mainmodel
import sys


def platform_config():
    """Performs any platform-specific configuration
    required for the application"""
    if sys.platform == 'win32' and mainmodel.is_win7():
    # Set taskbar icon to match application's icon
    # Code courtesy DamonJW
    # http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon
        import ctypes

        myappid = 'tri.nditoolbox.bane.1' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    platform_config()
    application = mainui.main()