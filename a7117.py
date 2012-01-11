__author__ = 'Chris R. Coughlin'

from views import mainui

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    application = mainui.main()