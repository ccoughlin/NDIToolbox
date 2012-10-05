"""workerthread.py - simple Thread wrapper for running long processes

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.mainmodel import get_logger
import threading
import sys

class WorkerThread(threading.Thread):
    """Daemon Thread wrapper to execute long-running processes"""

    def __init__(self, exception_queue, return_queue=None, group=None, target=None, name=None,
                 args=(), kwargs={}, verbose=None):
        """Standard Thread API with the addition of Queues for passing Exceptions
        and return values."""
        threading.Thread.__init__(self, group=group, target=target, name=name, verbose=verbose)
        self.daemon = True
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.exception_queue = exception_queue
        self.result_queue = return_queue

    def run(self):
        """Runs the target function.  Exceptions are returned
        in the instance's exception_queue as exception type, exception
        tuple (sys.exc_info()[:2].  Returns the target's return value
        if the instance's result_queue has been set."""
        try:
            retval = self.target(*self.args, **self.kwargs)
            if self.result_queue is not None:
                self.result_queue.put(retval)
        except Exception as err:
            # Pass a message to the calling thread with the Exception information
            self.exception_queue.put(sys.exc_info()[:2])
