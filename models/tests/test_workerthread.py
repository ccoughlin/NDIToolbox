"""test_workerthread.py - tests the workerthread module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import unittest
from models import workerthread
import Queue

class TestWorkerThread(unittest.TestCase):
    """Tests the WorkerThread class"""

    def sample_function(self, a, b):
        """Sample function to test WorkerThread execution"""
        return a + b

    def sample_exception_function(self, a, b):
        """Sample function to test handling Exceptions"""
        raise Exception("An error has occurred.")

    def setUp(self):
        self.message_queue = Queue.Queue()
        self.exception_queue = Queue.Queue()

    def test_execution(self):
        """Verify execution without Exceptions"""
        a_thread = workerthread.WorkerThread(exception_queue=self.exception_queue,
                                             return_queue=self.message_queue,
                                             target=self.sample_function, args=(1, 2))
        a_thread.start()
        a_thread.join()
        self.assertEqual(self.sample_function(1, 2), self.message_queue.get())

    def test_exception_execution(self):
        """Verify Exceptions are passed back through the Exception Queue"""
        a_thread = workerthread.WorkerThread(exception_queue=self.exception_queue,
                                             return_queue=self.message_queue,
                                             target=self.sample_exception_function, args=(1, 2))
        a_thread.start()
        a_thread.join()
        exc_type, exc = self.exception_queue.get()
        self.assertTrue(isinstance(exc, Exception))

if __name__ == "__main__":
    unittest.main()