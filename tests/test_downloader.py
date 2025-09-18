import unittest
import os
import hashlib
import http.server
import socketserver
import threading
import time
from tests.mcp_client import MCPClient

# Get the absolute path to the root of the repository
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class TestDownloader(unittest.TestCase):

    PORT = 8000
    TEST_FILE_NAME = "test_file.txt"
    TEST_FILE_CONTENT = "This is a test file for the downloader."

    httpd = None
    server_thread = None

    @classmethod
    def setUpClass(cls):
        # Create a test file
        with open(cls.TEST_FILE_NAME, "w") as f:
            f.write(cls.TEST_FILE_CONTENT)

        # Start a simple HTTP server in a separate thread
        handler = http.server.SimpleHTTPRequestHandler
        # Try to create the server, handling the case where the port is already in use
        for i in range(5):
            try:
                cls.httpd = socketserver.TCPServer(("", cls.PORT + i), handler)
                cls.PORT = cls.PORT + i # Update port to the one that worked
                break
            except OSError:
                print(f"Port {cls.PORT + i} is in use, trying next port.")

        if cls.httpd is None:
            raise RuntimeError("Could not find an open port for the test HTTP server.")

        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        # Stop the HTTP server
        if cls.httpd:
            cls.httpd.shutdown()
            cls.httpd.server_close()

        # Clean up the test file
        if os.path.exists(cls.TEST_FILE_NAME):
            os.remove(cls.TEST_FILE_NAME)


    def setUp(self):
        downloader_script_path = os.path.join(REPO_ROOT, 'downloader.py')
        self.client = MCPClient(server_command=["python3", downloader_script_path])
        self.client.start()

    def tearDown(self):
        self.client.stop()
        downloaded_file = os.path.basename(self.TEST_FILE_NAME)
        if os.path.exists(downloaded_file):
             os.remove(downloaded_file)


    def test_download_file(self):
        # Calculate the hash of the original file
        original_hash = hashlib.sha256(self.TEST_FILE_CONTENT.encode()).hexdigest()

        # Send a request to download the file
        url = f"http://localhost:{self.PORT}/{self.TEST_FILE_NAME}"
        request_id = self.client.send_json({"params": {"url": url}}, close_stdin=True)
        response = self.client.get_response(request_id)

        # Check the response from the server
        self.assertIsNotNone(response)
        self.assertEqual(response["result"]["status"], "success")

        # Verify that the file was downloaded
        downloaded_file = os.path.basename(self.TEST_FILE_NAME)
        self.assertTrue(os.path.exists(downloaded_file))

        # Verify the content of the downloaded file
        with open(downloaded_file, "r") as f:
            downloaded_content = f.read()

        downloaded_hash = hashlib.sha256(downloaded_content.encode()).hexdigest()

        self.assertEqual(downloaded_hash, original_hash)


if __name__ == '__main__':
    unittest.main()
