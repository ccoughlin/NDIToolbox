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
        parser.add_argument('-m', '--multiprocess', action='store_true', default=False,
                            help="Use multiple simultaneous processes for analysis")
        args = parser.parse_args()
        mainmodel.MainModel.check_user_path()
        available_plugins = mainmodel.load_plugins()
        available_plugins_names = [plugin[0] for plugin in available_plugins]
        if args.toolkit and args.toolkit not in available_plugins_names:
            print("** Unable to locate plugin '{0}'.  Available plugins:".format(args.toolkit))
            for plugin_name in available_plugins_names:
                print("\t{0}".format(plugin_name))
            sys.exit(1)
        workers = multiprocessing.Pool()
        if args.multiprocess:
            print("Using multiprocessing mode, {0} simultaneous processes".format(multiprocessing.cpu_count()))
        if args.input_files:
            for _f in args.input_files:
                    paths = glob.glob(_f)
                    for _p in paths:
                        if not args.multiprocess:
                            print("\nProcessing {0}...".format(_p))
                            if args.toolkit:
                                batchui_ctrl.run_plugin(toolkit=args.toolkit,
                                                        input_file=_p,
                                                        toolkit_config=args.toolkit_config,
                                                        file_type=args.filetype,
                                                        save_data=args.save_output)
                            else:
                                batchui_ctrl.import_data(input_file=_p, file_type=args.filetype)
                        else:
                            print("\nAdding {0} to job list...".format(_p))
                            if args.toolkit:
                                workers.apply_async(batchui_ctrl.run_plugin,
                                                    kwds={'toolkit':args.toolkit,
                                                          'input_file':_p,
                                                          'toolkit_config':args.toolkit_config,
                                                          'file_type':args.filetype,
                                                          'save_data':args.save_output})
                            else:
                                workers.apply_async(batchui_ctrl.import_data,
                                                    kwds={'input_file':_p,
                                                          'file_type':args.filetype})
            workers.close()
            workers.join()
    else:
        module_logger.info("Completed multiprocessing support.")
        platform_config()
        module_logger.info("Completed platform config, starting main UI.")
        application = mainui.main()