#!/usr/bin/env python3
import sys
import json
import subprocess
import os

# MCP Protocol Implementation
MCP_VERSION = "2024-11-05"

def send_response(id, result=None, error=None):
    """Sends a JSON-RPC response."""
    response = {"jsonrpc": "2.0", "id": id}
    if error:
        response["error"] = error
    else:
        response["result"] = result
    print(json.dumps(response), flush=True)

def send_notification(method, params=None):
    """Sends a JSON-RPC notification."""
    notification = {"jsonrpc": "2.0", "method": method}
    if params:
        notification["params"] = params
    print(json.dumps(notification), flush=True)

def handle_initialize(id, params):
    """Handle MCP initialize request."""
    send_response(id, {
        "protocolVersion": MCP_VERSION,
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "uber-apk-signer-mcp-server",
            "version": "1.0.0"
        }
    })

def handle_tools_list(id, params):
    """Handle tools/list request."""
    send_response(id, {
        "tools": [
            {
                "name": "sign_apk",
                "description": "Sign APK files using uber-apk-signer",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Arguments to pass to uber-apk-signer"
                        }
                    },
                    "required": ["args"]
                }
            }
        ]
    })

def handle_tools_call(id, params):
    """Handle tools/call request."""
    uber_apk_signer_path = "/usr/local/bin/uber-apk-signer.jar"
    
    # Check if the JAR file exists
    if not os.path.exists(uber_apk_signer_path):
        send_response(id, error={
            "code": -32000,
            "message": f"uber-apk-signer.jar not found at {uber_apk_signer_path}"
        })
        return
    
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        command_args = arguments.get("args", [])

        if tool_name != "sign_apk":
            send_response(id, error={
                "code": -32601,
                "message": f"Unknown tool: {tool_name}"
            })
            return

        # Execute uber-apk-signer with the provided arguments
        cmd = ["java", "-jar", uber_apk_signer_path] + command_args
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=60
        )
        
        output = f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        send_response(id, {
            "content": [
                {
                    "type": "text",
                    "text": output
                }
            ],
            "isError": process.returncode != 0
        })

    except subprocess.TimeoutExpired:
        send_response(id, error={
            "code": -32000,
            "message": "Command timed out after 60 seconds"
        })
    except Exception as e:
        send_response(id, error={
            "code": -32000,
            "message": str(e)
        })

def main():
    """Main loop to read requests and handle MCP protocol."""
    initialized = False
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            method = request.get("method")
            req_id = request.get("id")
            params = request.get("params", {})

            if method == "initialize":
                handle_initialize(req_id, params)
                initialized = True
            elif method == "initialized":
                # Client confirms initialization is complete
                continue
            elif not initialized:
                send_response(req_id, error={
                    "code": -32002,
                    "message": "Server not initialized"
                })
            elif method == "tools/list":
                handle_tools_list(req_id, params)
            elif method == "tools/call":
                handle_tools_call(req_id, params)
            else:
                send_response(req_id, error={
                    "code": -32601,
                    "message": f"Method not found: {method}"
                })

        except json.JSONDecodeError:
            if req_id:
                send_response(req_id, error={
                    "code": -32700,
                    "message": "Parse error"
                })
        except Exception as e:
            if req_id:
                send_response(req_id, error={
                    "code": -32000,
                    "message": str(e)
                })

if __name__ == "__main__":
    main()