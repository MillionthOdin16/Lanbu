#!/usr/bin/env python3
import sys
import json
import subprocess

def send_response(id, result):
    """Sends a JSON-RPC response."""
    response = {"jsonrpc": "2.0", "id": id, "result": result}
    # Use a separator to ensure the agent can split multiple JSON objects
    print(json.dumps(response) + '\n', flush=True)

def main():
    """Main loop to read requests and execute keytool commands."""
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        
        try:
            request = json.loads(line)
            req_id = request.get("id")
            params = request.get("params", {})
            command_args = params.get("args", [])

            # Execute keytool with the provided arguments
            process = subprocess.run(
                ["keytool"] + command_args,
                capture_output=True,
                text=True,
                check=False
            )
            
            output = f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
            send_response(req_id, {"output": output, "exitCode": process.returncode})

        except json.JSONDecodeError:
            # Handle cases where an invalid JSON line is received
            send_response(None, {"output": "Error: Invalid JSON received.", "exitCode": 1})
        except Exception as e:
            # Handle other potential errors during execution
            send_response(req_id, {"output": str(e), "exitCode": 1})

if __name__ == "__main__":
    main()
