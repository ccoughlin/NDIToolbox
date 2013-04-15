__author__ = 'Chris R. Coughlin'

from views import mainui
from models import mainmodel
from controllers import batchui_ctrl
import argparse
import glob
import multiprocessing
import sys

module_logger = mainmodel.get_logger(__name__)

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
    multiprocessing.freeze_support()
    if len(sys.argv) > 1:
        # Enter headless batch mode - given a list of input files, run a specified toolkit on each in turn
        print("\nNDIToolbox Batch Mode")
        parser = argparse.ArgumentParser(description='Run NDIToolbox toolkit in batch mode')
        parser.add_argument('-t', '--toolkit', help='Name of toolkit to run')
        parser.add_argument('-c', '--toolkit_config', help='Config file for toolkit')
        parser.add_argument('-f', '--filetype', help='Specify type of input file (default: guess from file extension)')
        parser.add_argument('-i', '--input_files', nargs=argparse.REMAINDER, help='Specify input file or files')
        parser.add_argument('-s', '--save_output', action='store_true', default=False,
                            help="Save plugin output to new HDF5 data file")
        args = parser.parse_args()
        mainmodel.MainModel.check_user_path()
        available_plugins = mainmodel.load_plugins()
        available_plugins_names = [plugin[0] for plugin in available_plugins]
        if args.toolkit and args.input_files:
            if args.toolkit in available_plugins_names:
                # TODO - more elegant way to handle specifying files whether the shell expands the wildcard or not - ?
                for _f in args.input_files:
                    paths = glob.glob(_f)
                    for _p in paths:
                        print("\tProcessing {0}...".format(_p))
                        # TODO - consider adding support for multiprocessing Pools - e.g. make default except if
                        # MemoryErrors encountered - files too large for multiprocessing, drop back to single process
                        batchui_ctrl.run_plugin(toolkit=args.toolkit, input_file=_p, toolkit_config=args.toolkit_config,
                                                file_type=args.filetype, save_data=args.save_output)
            else:
                print("** Unable to locate plugin '{0}'.  Available plugins:".format(args.toolkit))
                for plugin_name in available_plugins_names:
                    print("\t{0}".format(plugin_name))
    else:
        module_logger.info("Completed multiprocessing support.")
        platform_config()
        module_logger.info("Completed platform config, starting main UI.")
        application = mainui.main()