#!/usr/bin/env python3
import sys
import json
import subprocess
import os

def send_response(id, result):
    """Sends a JSON-RPC response."""
    response = {"jsonrpc": "2.0", "id": id, "result": result}
    # Use a separator to ensure the agent can split multiple JSON objects
    print(json.dumps(response) + '\n', flush=True)

def main():
    """Main loop to read requests and execute uber-apk-signer commands."""
    # Allow overriding the path for testing purposes
    uber_apk_signer_path = os.environ.get("UBER_APK_SIGNER_JAR_PATH", "/usr/local/bin/uber-apk-signer.jar")
    
    # Check if the JAR file exists
    if not os.path.exists(uber_apk_signer_path):
        print(f"Error: uber-apk-signer.jar not found at {uber_apk_signer_path}", file=sys.stderr)
        sys.exit(1)
    
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        
        req_id = None
        try:
            line = line.strip()
            if not line:
                continue

            request = json.loads(line)
            req_id = request.get("id")
            params = request.get("params", {})
            command_args = params.get("args", [])

            # Execute uber-apk-signer with the provided arguments
            # The command will be: java -jar [uber_apk_signer_path] [args]
            cmd = ["java", "-jar", uber_apk_signer_path] + command_args
            
            process = subprocess.run(
                cmd,
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