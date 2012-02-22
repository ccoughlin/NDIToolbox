"""test_fetcher.py - tests the fetcher module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import fetcher
import unittest
import os.path
import random
import string
import SimpleHTTPServer
import SocketServer
import threading
import urllib

class TestFetcher(unittest.TestCase):
    """Tests the Fetcher class"""

    @classmethod
    def setUpClass(cls):
        """Create a SimpleHTTPServer instance to serve
        test files from the suport_files folder"""
        PORT = 8000 + random.randint(1, 1000)
        req_handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        cls.httpd = SocketServer.TCPServer(("localhost", PORT), req_handler)
        cls.httpd.timeout = 5
        # Handle server path differences between running these
        # tests directly vs. running the project test suite
        cur_dir = os.getcwd()
        if os.path.normcase(cur_dir) == os.path.normcase(os.path.dirname(__file__)):
            # Running this test module directly
            cls.local_file = os.path.join('support_files', 'LAHMPlogo.png')
        else:
            # Running as part of larger project test suite
            cls.local_file = os.path.join('models', 'tests',
                                          'support_files', 'LAHMPlogo.png')
        cls.data_file = urllib.pathname2url(cls.local_file)
        cls.data_url = 'http://localhost:{0}/{1}'.format(PORT, cls.data_file)

    def setUp(self):
        """Creates a SimpleHTTPServer instance to handle a single
        request.  Use self.server_proc.start() to initiate."""
        self.server_thd = threading.Thread(target=TestFetcher.httpd.handle_request)

    def test_init(self):
        """Verify initial member settings"""
        a_fetcher = fetcher.Fetcher(url=TestFetcher.data_url)
        self.assertEqual(a_fetcher.url, TestFetcher.data_url)
        self.assertIsNone(a_fetcher.username)
        self.assertIsNone(a_fetcher.password)
        available_chars = [char for char in string.ascii_letters + string.digits]
        uname = random.shuffle(available_chars)
        pw = random.shuffle(available_chars)
        another_fetcher = fetcher.Fetcher(url=TestFetcher.data_url, username=uname,
                                          password=pw)
        self.assertEqual(another_fetcher.username, uname)
        self.assertEqual(another_fetcher.password, pw)

    def test_fetch_handle(self):
        """Verify returning file-like object handle to remote file"""
        a_fetcher = fetcher.Fetcher(url=TestFetcher.data_url)
        self.server_thd.start()
        retrieved_file = a_fetcher.fetch_handle().read()
        with open(TestFetcher.local_file, 'rb') as fidin:
            local_file = fidin.read()
            self.assertEqual(local_file, retrieved_file)

    def test_bad_fetch_handle(self):
        """Verify IOError exception raised when a
        server isn't found or can't fulfill the request."""
        no_such_file = TestFetcher.data_url + ".org"
        a_fetcher = fetcher.Fetcher(url=no_such_file)
        self.server_thd.start()
        with self.assertRaises(IOError):
            a_fetcher.fetch()

    def test_fetch(self):
        """Verify fetching remote file"""
        a_fetcher = fetcher.Fetcher(url=TestFetcher.data_url, username='bert',
                                    password='ernie')
        self.server_thd.start()
        retrieved_file = a_fetcher.fetch()
        with open(TestFetcher.local_file, 'rb') as fidin:
            local_file = fidin.read()
            self.assertEqual(local_file, retrieved_file)

    def test_bad_fetch(self):
        """Verify IOError exception raised when a
        server isn't found or can't fulfill the request."""
        no_such_file = TestFetcher.data_url + ".org"
        a_fetcher = fetcher.Fetcher(url=no_such_file)
        self.server_thd.start()
        with self.assertRaises(IOError):
            a_fetcher.fetch()

    def tearDown(self):
        """Shuts down the server process if still active"""
        if self.server_thd.is_alive():
            self.server_thd.join()

if __name__ == "__main__":
    random.seed()
    unittest.main()