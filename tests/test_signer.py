import unittest
import os
import subprocess
import requests
from tests.mcp_client import MCPClient

# Get the absolute path to the root of the repository
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BIN_DIR = os.path.join(os.path.dirname(__file__), 'bin')

class TestSigner(unittest.TestCase):

    KEYSTORE_FILE = "test_signer.keystore"
    KEYSTORE_PASS = "password"
    KEY_ALIAS = "testsignerkey"
    UBER_APK_SIGNER_URL = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar"
    UBER_APK_SIGNER_JAR = os.path.join(BIN_DIR, "uber-apk-signer.jar")
    INPUT_APK = "com.Glowbeast.LanBu v0.53.apk"
    SIGNED_APK_SUFFIX = "-aligned-signed.apk"


    @classmethod
    def setUpClass(cls):
        # Create bin directory if it doesn't exist
        os.makedirs(BIN_DIR, exist_ok=True)

        # Download uber-apk-signer.jar
        if not os.path.exists(cls.UBER_APK_SIGNER_JAR):
            print("Downloading uber-apk-signer.jar...")
            response = requests.get(cls.UBER_APK_SIGNER_URL, allow_redirects=True)
            response.raise_for_status()
            with open(cls.UBER_APK_SIGNER_JAR, 'wb') as f:
                f.write(response.content)
            print("Download complete.")

        # Generate a keystore
        if os.path.exists(cls.KEYSTORE_FILE):
            os.remove(cls.KEYSTORE_FILE)

        genkey_args = [
            "-genkeypair", "-keystore", cls.KEYSTORE_FILE,
            "-storepass", cls.KEYSTORE_PASS, "-keypass", cls.KEYSTORE_PASS,
            "-alias", cls.KEY_ALIAS, "-dname", "CN=Test, OU=Test, O=Test, L=Test, S=Test, C=US",
            "-keyalg", "RSA", "-keysize", "2048", "-validity", "365"
        ]
        subprocess.run(["keytool"] + genkey_args, check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        # Clean up downloaded files and generated keystore
        if os.path.exists(cls.UBER_APK_SIGNER_JAR):
            os.remove(cls.UBER_APK_SIGNER_JAR)
        if os.path.exists(cls.KEYSTORE_FILE):
            os.remove(cls.KEYSTORE_FILE)

        base_name = os.path.splitext(os.path.basename(cls.INPUT_APK))[0]
        signed_apk_path = base_name + cls.SIGNED_APK_SUFFIX
        if os.path.exists(signed_apk_path):
            os.remove(signed_apk_path)


    def setUp(self):
        # Set environment variable for the JAR path
        os.environ["UBER_APK_SIGNER_JAR_PATH"] = self.UBER_APK_SIGNER_JAR

        signer_script_path = os.path.join(REPO_ROOT, 'uber-apk-signer-mcp-server.py')
        self.signer_client = MCPClient(server_command=["python3", signer_script_path])
        self.signer_client.start()

        keytool_script_path = os.path.join(REPO_ROOT, 'keytool-mcp-server.py')
        self.keytool_client = MCPClient(server_command=["python3", keytool_script_path])
        self.keytool_client.start()

    def tearDown(self):
        self.signer_client.stop()
        self.keytool_client.stop()


    def test_sign_apk_and_verify(self):
        # 1. Sign the APK
        sign_args = [
            "--apks", self.INPUT_APK,
            "--out", ".",
            "--ks", self.KEYSTORE_FILE,
            "--ksPass", self.KEYSTORE_PASS,
            "--ksAlias", self.KEY_ALIAS,
            "--ksKeyPass", self.KEYSTORE_PASS,
            "--allowResign"
        ]

        request_id_sign = self.signer_client.send_json({"params": {"args": sign_args}}, close_stdin=True)
        response_sign = self.signer_client.get_response(request_id_sign, timeout=30)

        print(f"Signer output:\n{response_sign['result']['output']}")

        self.assertIsNotNone(response_sign, "Did not receive a response from signer command")
        self.assertEqual(response_sign["result"]["exitCode"], 0, f"Signer exited with non-zero status. Output:\n{response_sign['result']['output']}")

        # Verify that the signed APK was created
        base_name = os.path.splitext(os.path.basename(self.INPUT_APK))[0]
        signed_apk_path = base_name + self.SIGNED_APK_SUFFIX

        self.assertTrue(os.path.exists(signed_apk_path), f"Signed APK file '{signed_apk_path}' was not created. Files in dir: {os.listdir('.')}")

        # 2. Verify the signature
        self.keytool_client.stop()
        keytool_script_path = os.path.join(REPO_ROOT, 'keytool-mcp-server.py')
        self.keytool_client = MCPClient(server_command=["python3", keytool_script_path])
        self.keytool_client.start()

        verify_args = [
            "-printcert",
            "-jarfile", signed_apk_path
        ]

        request_id_verify = self.keytool_client.send_json({"params": {"args": verify_args}}, close_stdin=True)
        response_verify = self.keytool_client.get_response(request_id_verify, timeout=20)

        self.assertIsNotNone(response_verify, "Did not receive a response from keytool verify command")
        self.assertEqual(response_verify["result"]["exitCode"], 0, f"Keytool verify exited with non-zero status. Output:\n{response_verify['result']['output']}")

        self.assertIn("Owner: CN=Test", response_verify["result"]["output"])

        if signed_apk_path and os.path.exists(signed_apk_path):
            os.remove(signed_apk_path)


if __name__ == '__main__':
    unittest.main()
