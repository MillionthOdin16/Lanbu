#!/usr/bin/env python3
import sys
import json
import requests
import os
from urllib.parse import urlparse

def send_response(id, result):
    """Sends a JSON-RPC response."""
    response = {"jsonrpc": "2.0", "id": id, "result": result}
    print(json.dumps(response) + '\n', flush=True)

def main():
    """Main loop to read requests and download files."""
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        
        try:
            request = json.loads(line)
            req_id = request.get("id")
            params = request.get("params", {})
            url = params.get("url")

            if not url:
                send_response(req_id, {"status": "error", "message": "URL parameter is missing."})
                continue

            # Default to saving in the current directory (/workspace)
            output_dir = os.getcwd()
            filename = os.path.basename(urlparse(url).path)
            output_path = os.path.join(output_dir, filename)

            # Download the file
            response = requests.get(url, stream=True)
            response.raise_for_status() # Raise an exception for bad status codes

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            send_response(req_id, {"status": "success", "message": f"File downloaded successfully to {output_path}"})

        except Exception as e:
            send_response(req_id, {"status": "error", "message": str(e)})

if __name__ == "__main__":
    main()
