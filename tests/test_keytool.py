import unittest
import os
from tests.mcp_client import MCPClient

# Get the absolute path to the root of the repository
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class TestKeytool(unittest.TestCase):

    KEYSTORE_FILE = "test.keystore"
    KEYSTORE_PASS = "password"
    KEY_ALIAS = "testkey"

    def setUp(self):
        # Ensure the keystore file doesn't exist before a test
        if os.path.exists(self.KEYSTORE_FILE):
            os.remove(self.KEYSTORE_FILE)

    def tearDown(self):
        # Clean up the keystore file after a test
        if os.path.exists(self.KEYSTORE_FILE):
            os.remove(self.KEYSTORE_FILE)

    def test_generate_and_verify_key(self):
        keytool_script_path = os.path.join(REPO_ROOT, 'keytool-mcp-server.py')

        # 1. Generate a new key
        client_gen = MCPClient(server_command=["python3", keytool_script_path])
        client_gen.start()

        genkey_args = [
            "-genkeypair",
            "-keystore", self.KEYSTORE_FILE,
            "-storepass", self.KEYSTORE_PASS,
            "-keypass", self.KEYSTORE_PASS,
            "-alias", self.KEY_ALIAS,
            "-dname", "CN=Test, OU=Test, O=Test, L=Test, S=Test, C=US",
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "365"
        ]

        request_id_gen = client_gen.send_json({"params": {"args": genkey_args}}, close_stdin=True)
        response_gen = client_gen.get_response(request_id_gen, timeout=20) # Genkey can be slow
        client_gen.stop()

        self.assertIsNotNone(response_gen, "Did not receive a response from genkey command")
        self.assertEqual(response_gen["result"]["exitCode"], 0, f"Keytool genkey exited with non-zero status. STDERR:\n{response_gen['result']['output']}")

        # Verify that the keystore file was created
        self.assertTrue(os.path.exists(self.KEYSTORE_FILE), "Keystore file was not created")

        # 2. Verify the key exists by listing the contents of the keystore
        client_list = MCPClient(server_command=["python3", keytool_script_path])
        client_list.start()

        list_args = [
            "-list",
            "-keystore", self.KEYSTORE_FILE,
            "-storepass", self.KEYSTORE_PASS,
        ]

        request_id_list = client_list.send_json({"params": {"args": list_args}}, close_stdin=True)
        response_list = client_list.get_response(request_id_list)
        client_list.stop()

        self.assertIsNotNone(response_list, "Did not receive a response from list command")
        self.assertEqual(response_list["result"]["exitCode"], 0, f"Keytool list exited with non-zero status. STDERR:\n{response_list['result']['output']}")

        # Check that the alias is in the output
        self.assertIn(self.KEY_ALIAS, response_list["result"]["output"])


if __name__ == '__main__':
    unittest.main()
