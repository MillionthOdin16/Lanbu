import subprocess
import json
import threading
import queue
import time
import requests
import sseclient

class StdioMCPClient:
    def __init__(self, server_command):
        self.server_command = server_command
        self.process = None
        self.request_id = 0
        self.response_queue = queue.Queue()
        self.stdout_thread = None
        self.stderr_thread = None
        self.initialized = False
        self.process_env = None

    def start(self):
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1, # Line-buffered
            env=self.process_env
        )
        self.stdout_thread = threading.Thread(target=self._read_stdout)
        self.stdout_thread.daemon = True
        self.stdout_thread.start()

        self.stderr_thread = threading.Thread(target=self._read_stderr)
        self.stderr_thread.daemon = True
        self.stderr_thread.start()
        time.sleep(2)

    def _read_stdout(self):
        for line in iter(self.process.stdout.readline, ''):
            try:
                response = json.loads(line)
                self.response_queue.put(response)
            except json.JSONDecodeError:
                print(f"StdioMCPClient Non-JSON stdout: {line.strip()}", flush=True)

    def _read_stderr(self):
        for line in iter(self.process.stderr.readline, ''):
            print(f"StdioMCPClient STDERR: {line.strip()}", flush=True)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

    def initialize(self, params):
        if self.initialized:
            return

        init_id = self.send_request("initialize", params)
        response = self.get_response(init_id)
        if response is not None:
            self.send_notification("notifications/initialized", {})
            time.sleep(5)
            self.initialized = True
        return response

    def send_notification(self, method, params):
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        request_json = json.dumps(request) + '\n'
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

    def send_request(self, method, params):
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        request_json = json.dumps(request) + '\n'
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        return self.request_id

    def get_response(self, request_id, timeout=20):
        start_time = time.time()
        temp_queue = []
        while time.time() - start_time < timeout:
            try:
                response = self.response_queue.get(timeout=1)
                if response.get("id") == request_id:
                    for item in temp_queue:
                        self.response_queue.put(item)
                    return response
                else:
                    temp_queue.append(response)
            except queue.Empty:
                pass

        for item in temp_queue:
            self.response_queue.put(item)
        return None

# Keep the old clients for the other tests
class MCPClient(StdioMCPClient):
    def send_json(self, data, close_stdin=False):
        if 'id' not in data:
            self.request_id += 1
            data['id'] = self.request_id

        request_json = json.dumps(data)

        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        if close_stdin:
            self.process.stdin.close()

        return data['id']

    def _read_stdout(self):
        # This is the version for the simple, broken servers
        try:
            stdout_data = self.process.stdout.read()
            if stdout_data:
                for line in stdout_data.strip().split('\n'):
                    try:
                        response = json.loads(line)
                        self.response_queue.put(response)
                    except json.JSONDecodeError:
                        print(f"MCPClient Non-JSON stdout: {line.strip()}", flush=True)
        except IOError:
            pass

class HTTPMCPClient(MCPClient):
    # This class is kept for now but is not used by the apktool test anymore.
    def __init__(self, server_command_template, port_range=(8652, 8672)):
        #...
        pass

    def start(self):
        # ... implementation from before ...
        pass

    # ... other methods ...
    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
