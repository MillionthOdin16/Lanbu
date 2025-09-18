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
    sys.stderr.write(f"Sent response for id {id}\n")
    sys.stderr.flush()

def main():
    """Main loop to read requests and download files."""
    sys.stderr.write("Downloader server started\n")
    sys.stderr.flush()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        
        req_id = None # Initialize req_id
        try:
            line = line.strip() # Strip whitespace
            if not line: # Skip empty lines
                continue

            sys.stderr.write(f"Read line: {line}\n")
            sys.stderr.flush()

            request = json.loads(line)
            req_id = request.get("id")
            sys.stderr.write(f"Processing request id {req_id}\n")
            sys.stderr.flush()

            params = request.get("params", {})
            url = params.get("url")

            if not url:
                send_response(req_id, {"status": "error", "message": "URL parameter is missing."})
                continue

            # Default to saving in the current directory (/workspace)
            output_dir = os.getcwd()
            filename = os.path.basename(urlparse(url).path)
            output_path = os.path.join(output_dir, filename)

            sys.stderr.write(f"Downloading {url} to {output_path}\n")
            sys.stderr.flush()

            # Download the file
            response = requests.get(url, stream=True)
            response.raise_for_status() # Raise an exception for bad status codes

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            sys.stderr.write(f"Download complete\n")
            sys.stderr.flush()

            send_response(req_id, {"status": "success", "message": f"File downloaded successfully to {output_path}"})

        except Exception as e:
            sys.stderr.write(f"Error processing request: {e}\n")
            sys.stderr.flush()
            send_response(req_id, {"status": "error", "message": str(e)})

if __name__ == "__main__":
    main()
