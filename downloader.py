#!/usr/bin/env python3
import sys
import json
import requests
import os
from urllib.parse import urlparse

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
            "name": "downloader-mcp-server",
            "version": "1.0.0"
        }
    })

def handle_tools_list(id, params):
    """Handle tools/list request."""
    send_response(id, {
        "tools": [
            {
                "name": "download_file",
                "description": "Download a file from a URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the file to download"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Full path where to save the file"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Optional filename to save as (if output_path not specified)"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "get_url_info",
                "description": "Get information about a URL without downloading",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to get information about"
                        }
                    },
                    "required": ["url"]
                }
            }
        ]
    })

def handle_tools_call(id, params):
    """Handle tools/call request."""
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "download_file":
            url = arguments.get("url")
            output_path = arguments.get("output_path")
            custom_filename = arguments.get("filename")

            if not url:
                send_response(id, error={
                    "code": -32602,
                    "message": "URL parameter is required"
                })
                return

            # Determine output path
            if output_path:
                # Use specified output path
                final_path = output_path
            else:
                # Default to saving in the current directory
                output_dir = os.getcwd()
                
                if custom_filename:
                    filename = custom_filename
                else:
                    filename = os.path.basename(urlparse(url).path)
                    if not filename:
                        filename = "downloaded_file"
                
                final_path = os.path.join(output_dir, filename)

            # Download the file
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(final_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(final_path)
            send_response(id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"File downloaded successfully to {final_path}\nSize: {file_size} bytes\nContent-Type: {response.headers.get('content-type', 'unknown')}"
                    }
                ],
                "isError": False
            })

        elif tool_name == "get_url_info":
            url = arguments.get("url")

            if not url:
                send_response(id, error={
                    "code": -32602,
                    "message": "URL parameter is required"
                })
                return

            # Get URL information with HEAD request
            response = requests.head(url, timeout=10)
            response.raise_for_status()
            
            info = {
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_length": response.headers.get('content-length', 'unknown'),
                "content_type": response.headers.get('content-type', 'unknown')
            }
            
            send_response(id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"URL Information:\n{json.dumps(info, indent=2)}"
                    }
                ],
                "isError": False
            })

        else:
            send_response(id, error={
                "code": -32601,
                "message": f"Unknown tool: {tool_name}"
            })

    except requests.RequestException as e:
        send_response(id, error={
            "code": -32000,
            "message": f"Download failed: {str(e)}"
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
