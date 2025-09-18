import unittest
import os
import shutil
import tempfile
import time
import subprocess
import json
from tests.mcp_client import StdioMCPClient

# Get the absolute path to the root of the repository
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APK_PATH = os.path.join(REPO_ROOT, "com.Glowbeast.LanBu v0.53.apk")
BIN_DIR = os.path.join(os.path.dirname(__file__), 'bin')
APKTOOL_SERVER_REPO = "https://github.com/zinja-coder/apktool-mcp-server.git"
APKTOOL_SERVER_DIR = os.path.join(BIN_DIR, "apktool-mcp-server")
APKTOOL_JAR_URL = "https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar"
APKTOOL_JAR = os.path.join(BIN_DIR, "apktool.jar")
APKTOOL_SCRIPT = os.path.join(BIN_DIR, "apktool")


class TestApktool(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs(BIN_DIR, exist_ok=True)

        # Download and set up apktool
        if not os.path.exists(APKTOOL_JAR):
            print("Downloading apktool.jar...")
            subprocess.run(["wget", APKTOOL_JAR_URL, "-O", APKTOOL_JAR], check=True, capture_output=True)
            print("Download complete.")

        with open(APKTOOL_SCRIPT, "w") as f:
            f.write(f"#!/bin/sh\njava -jar {APKTOOL_JAR} \"$@\"")
        os.chmod(APKTOOL_SCRIPT, 0o755)

        # Clone and set up apktool-mcp-server
        if not os.path.exists(APKTOOL_SERVER_DIR):
            print("Cloning apktool-mcp-server...")
            subprocess.run(["git", "clone", APKTOOL_SERVER_REPO, APKTOOL_SERVER_DIR], check=True, capture_output=True)
            print("Clone complete.")
            req_file = os.path.join(APKTOOL_SERVER_DIR, "requirements.txt")
            with open(req_file, 'r') as f:
                lines = f.readlines()
            with open(req_file, 'w') as f:
                for line in lines:
                    if 'logging' not in line:
                        f.write(line)
            subprocess.run(["pip", "install", "-r", req_file], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(BIN_DIR):
            shutil.rmtree(BIN_DIR)

    def setUp(self):
        self.workspace_dir = tempfile.mkdtemp()
        self.server_script = os.path.join(APKTOOL_SERVER_DIR, "apktool_mcp_server.py")

        self.env = os.environ.copy()
        self.env["PATH"] = f"{BIN_DIR}:{self.env['PATH']}"

        self.client = StdioMCPClient(server_command=[
            "python3", self.server_script,
            "--workspace", self.workspace_dir
        ])
        self.client.process_env = self.env
        self.client.start()

    def tearDown(self):
        self.client.stop()
        shutil.rmtree(self.workspace_dir)

    def test_full_cycle(self):
        # Initialize
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
        init_resp = self.client.initialize(init_params)
        self.assertIsNotNone(init_resp, "Did not receive response for initialize")

        # 1. Decode APK
        decode_params = {"name": "decode_apk", "arguments": {"apk_path": APK_PATH, "force": True}}
        decode_req_id = self.client.send_request("tools/call", decode_params)
        decode_resp = self.client.get_response(decode_req_id, timeout=60)
        self.assertIsNotNone(decode_resp)

        result_text = decode_resp['result']['content'][0]['text']
        result_data = json.loads(result_text)
        self.assertTrue(result_data["success"], f"Decode failed: {result_data.get('error')}")
        project_dir = result_data["output_dir"]

        self.assertTrue(os.path.isdir(project_dir))
        self.assertTrue(os.path.exists(os.path.join(project_dir, "AndroidManifest.xml")))

        # 2. Get Manifest
        manifest_params = {"name": "get_manifest", "arguments": {"project_dir": project_dir}}
        manifest_req_id = self.client.send_request("tools/call", manifest_params)
        manifest_resp = self.client.get_response(manifest_req_id)
        result_text = manifest_resp['result']['content'][0]['text']
        result_data = json.loads(result_text)
        self.assertTrue(result_data["success"])
        original_manifest = result_data["manifest"]
        self.assertIn("com.Glowbeast.LanBu", original_manifest)

        # 3. Modify strings.xml
        strings_path = os.path.join(project_dir, "res", "values", "strings.xml")
        with open(strings_path, "r") as f:
            original_strings = f.read()

        new_strings = original_strings.replace("LanBu", "LanBu_MODIFIED")

        modify_params = {
            "name": "modify_resource_file",
            "arguments": {
                "project_dir": project_dir,
                "resource_type": "values",
                "resource_name": "strings.xml",
                "new_content": new_strings,
                "create_backup": False
            }
        }
        modify_req_id = self.client.send_request("tools/call", modify_params)
        modify_resp = self.client.get_response(modify_req_id)
        result_text = modify_resp['result']['content'][0]['text']
        result_data = json.loads(result_text)
        self.assertTrue(result_data["success"])

        # Verify modification
        with open(strings_path, "r") as f:
            modified_strings_from_disk = f.read()
        self.assertEqual(new_strings, modified_strings_from_disk)

        # 4. Rebuild APK
        build_params = {"name": "build_apk", "arguments": {"project_dir": project_dir}}
        build_req_id = self.client.send_request("tools/call", build_params)
        build_resp = self.client.get_response(build_req_id, timeout=60)
        result_text = build_resp['result']['content'][0]['text']
        result_data = json.loads(result_text)
        self.assertTrue(result_data["success"])

        built_apk_path = result_data["apk_path"]
        self.assertTrue(os.path.exists(built_apk_path))

if __name__ == '__main__':
    unittest.main()
