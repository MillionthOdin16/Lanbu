import subprocess
import json
import time

def main():
    server_command = ["python3", "downloader.py"]
    process = subprocess.Popen(
        server_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(1)

    # Send a request without a newline
    request = {"id": 1, "params": {"url": "http://example.com/somefile.txt"}}
    request_json = json.dumps(request)

    print(f"Sending request: {request_json.strip()}")

    if process.poll() is None:
        process.stdin.write(request_json)
        process.stdin.flush()
        process.stdin.close()
    else:
        print("Process terminated prematurely.")
        return

    print("Waiting for response...")
    response_line = process.stdout.readline()
    print(f"Received response: {response_line.strip()}")

    process.wait(timeout=5)
    stderr_output = process.stderr.read()
    print(f"Stderr output:\n{stderr_output}")

if __name__ == "__main__":
    main()
