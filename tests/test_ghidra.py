import unittest
import os
import shutil
import tempfile
import time
import subprocess
import json
from tests.mcp_client import StdioMCPClient

class TestGhidra(unittest.TestCase):

    def setUp(self):
        # The pyghidra-mcp server needs GHIDRA_INSTALL_DIR to be set.
        # In the Dockerfile, it's /opt/ghidra.
        if "GHIDRA_INSTALL_DIR" not in os.environ:
            self.skipTest("GHIDRA_INSTALL_DIR environment variable not set. Skipping Ghidra tests.")
            return

        self.client = StdioMCPClient(server_command=[
            "pyghidra-mcp", "/bin/ls"
        ])
        self.client.start()

    def tearDown(self):
        if self.client:
            self.client.stop()

    def test_ghidra_analysis(self):
        # Initialize
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
        init_resp = self.client.initialize(init_params)
        self.assertIsNotNone(init_resp, "Did not receive response for initialize")

        # List binaries
        list_params = {"name": "list_project_binaries", "arguments": {}}
        list_req_id = self.client.send_request("tools/call", list_params)
        list_resp = self.client.get_response(list_req_id, timeout=60)
        self.assertIsNotNone(list_resp)
        result_text = list_resp['result']['content'][0]['text']
        result_data = json.loads(result_text)
        self.assertIn("ls", result_data)

        # Decompile the 'main' function
        decompile_params = {"name": "decompile_function", "arguments": {"binary_name": "ls", "name": "main"}}
        decompile_req_id = self.client.send_request("tools/call", decompile_params)
        decompile_resp = self.client.get_response(decompile_req_id, timeout=60)
        self.assertIsNotNone(decompile_resp)
        result_text = decompile_resp['result']['content'][0]['text']
        result_data = json.loads(result_text)
        self.assertIn("main", result_data)
        self.assertIn("argc", result_data) # Check for some C-like code
        self.assertIn("argv", result_data)


if __name__ == '__main__':
    unittest.main()
