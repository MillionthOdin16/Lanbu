#!/usr/bin/env python3
import sys
import json
import subprocess

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
            "name": "keytool-mcp-server",
            "version": "1.0.0"
        }
    })

def handle_tools_list(id, params):
    """Handle tools/list request."""
    send_response(id, {
        "tools": [
            {
                "name": "generate_keystore",
                "description": "Generate a new keystore with a key pair",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keystore_path": {
                            "type": "string",
                            "description": "Path where to save the keystore"
                        },
                        "alias": {
                            "type": "string",
                            "description": "Alias for the key pair"
                        },
                        "dname": {
                            "type": "string",
                            "description": "Distinguished name (e.g. 'CN=Test, O=Org, C=US')"
                        },
                        "keypass": {
                            "type": "string",
                            "description": "Password for the private key"
                        },
                        "storepass": {
                            "type": "string",
                            "description": "Password for the keystore"
                        },
                        "validity": {
                            "type": "string",
                            "description": "Validity period in days (default: 365)"
                        }
                    },
                    "required": ["keystore_path", "alias", "dname", "keypass", "storepass"]
                }
            },
            {
                "name": "list_keystore",
                "description": "List contents of a keystore",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keystore_path": {
                            "type": "string",
                            "description": "Path to the keystore file"
                        },
                        "storepass": {
                            "type": "string",
                            "description": "Password for the keystore"
                        }
                    },
                    "required": ["keystore_path", "storepass"]
                }
            },
            {
                "name": "export_certificate",
                "description": "Export a certificate from keystore",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keystore_path": {
                            "type": "string",
                            "description": "Path to the keystore file"
                        },
                        "alias": {
                            "type": "string",
                            "description": "Alias of the certificate to export"
                        },
                        "cert_path": {
                            "type": "string",
                            "description": "Path where to save the certificate"
                        },
                        "storepass": {
                            "type": "string",
                            "description": "Password for the keystore"
                        }
                    },
                    "required": ["keystore_path", "alias", "cert_path", "storepass"]
                }
            },
            {
                "name": "keytool_command",
                "description": "Execute custom keytool command",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Arguments to pass to keytool"
                        }
                    },
                    "required": ["args"]
                }
            }
        ]
    })

def handle_tools_call(id, params):
    """Handle tools/call request."""
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "generate_keystore":
            keystore_path = arguments.get("keystore_path")
            alias = arguments.get("alias")
            dname = arguments.get("dname")
            keypass = arguments.get("keypass")
            storepass = arguments.get("storepass")
            validity = arguments.get("validity", "365")
            
            # Build keytool command for keystore generation
            cmd = [
                "keytool", "-genkeypair",
                "-alias", alias,
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-dname", dname,
                "-keypass", keypass,
                "-keystore", keystore_path,
                "-storepass", storepass,
                "-validity", validity
            ]
            
        elif tool_name == "list_keystore":
            keystore_path = arguments.get("keystore_path")
            storepass = arguments.get("storepass")
            
            cmd = [
                "keytool", "-list",
                "-keystore", keystore_path,
                "-storepass", storepass
            ]
            
        elif tool_name == "export_certificate":
            keystore_path = arguments.get("keystore_path")
            alias = arguments.get("alias")
            cert_path = arguments.get("cert_path")
            storepass = arguments.get("storepass")
            
            cmd = [
                "keytool", "-exportcert",
                "-alias", alias,
                "-keystore", keystore_path,
                "-storepass", storepass,
                "-file", cert_path
            ]
            
        elif tool_name == "keytool_command":
            command_args = arguments.get("args", [])
            cmd = ["keytool"] + command_args
            
        else:
            send_response(id, error={
                "code": -32601,
                "message": f"Unknown tool: {tool_name}"
            })
            return

        # Execute keytool command
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=60
        )
        
        output = f"Command: {' '.join(cmd)}\n\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}\nExit Code: {process.returncode}"
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
