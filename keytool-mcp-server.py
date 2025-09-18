#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import shutil
from pathlib import Path

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

def check_keytool_availability():
    """Check if keytool is available in the system."""
    return shutil.which("keytool") is not None

def validate_keystore_path(keystore_path):
    """Validate keystore path and create directory if needed."""
    try:
        parent_dir = os.path.dirname(keystore_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        return True, None
    except Exception as e:
        return False, str(e)

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
                "description": "Generate a new keystore with a key pair for APK signing",
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
                        },
                        "keyalg": {
                            "type": "string",
                            "description": "Key algorithm (default: RSA)"
                        },
                        "keysize": {
                            "type": "string",
                            "description": "Key size in bits (default: 2048)"
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
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed information"
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
                        },
                        "format": {
                            "type": "string",
                            "description": "Certificate format (DER or PEM, default: DER)"
                        }
                    },
                    "required": ["keystore_path", "alias", "cert_path", "storepass"]
                }
            },
            {
                "name": "import_certificate",
                "description": "Import a certificate into keystore",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keystore_path": {
                            "type": "string",
                            "description": "Path to the keystore file"
                        },
                        "alias": {
                            "type": "string",
                            "description": "Alias for the imported certificate"
                        },
                        "cert_path": {
                            "type": "string",
                            "description": "Path to the certificate file to import"
                        },
                        "storepass": {
                            "type": "string",
                            "description": "Password for the keystore"
                        },
                        "noprompt": {
                            "type": "boolean",
                            "description": "Don't prompt for confirmation (default: true)"
                        }
                    },
                    "required": ["keystore_path", "alias", "cert_path", "storepass"]
                }
            },
            {
                "name": "delete_entry",
                "description": "Delete an entry from keystore",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keystore_path": {
                            "type": "string",
                            "description": "Path to the keystore file"
                        },
                        "alias": {
                            "type": "string",
                            "description": "Alias of the entry to delete"
                        },
                        "storepass": {
                            "type": "string",
                            "description": "Password for the keystore"
                        }
                    },
                    "required": ["keystore_path", "alias", "storepass"]
                }
            },
            {
                "name": "check_tool_availability",
                "description": "Check if keytool is available on the system",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "keytool_command",
                "description": "Execute custom keytool command with arguments",
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

        if tool_name == "check_tool_availability":
            # Check if keytool is available
            available = check_keytool_availability()
            keytool_path = shutil.which("keytool") if available else None
            
            result = {
                "available": available,
                "path": keytool_path,
                "java_home": os.environ.get("JAVA_HOME", "Not set")
            }
            
            send_response(id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"Keytool Availability Check:\n{json.dumps(result, indent=2)}"
                    }
                ],
                "isError": False
            })
            return

        # Check if keytool is available for other operations
        if not check_keytool_availability():
            send_response(id, error={
                "code": -32000,
                "message": "keytool is not available. Please ensure Java JDK is installed and keytool is in PATH."
            })
            return

        if tool_name == "generate_keystore":
            keystore_path = arguments.get("keystore_path")
            alias = arguments.get("alias")
            dname = arguments.get("dname")
            keypass = arguments.get("keypass")
            storepass = arguments.get("storepass")
            validity = arguments.get("validity", "365")
            keyalg = arguments.get("keyalg", "RSA")
            keysize = arguments.get("keysize", "2048")
            
            # Validate keystore path
            is_valid, error_msg = validate_keystore_path(keystore_path)
            if not is_valid:
                send_response(id, error={
                    "code": -32602,
                    "message": f"Invalid keystore path: {error_msg}"
                })
                return
            
            # Build keytool command for keystore generation
            cmd = [
                "keytool", "-genkeypair",
                "-alias", alias,
                "-keyalg", keyalg,
                "-keysize", keysize,
                "-dname", dname,
                "-keypass", keypass,
                "-keystore", keystore_path,
                "-storepass", storepass,
                "-validity", validity
            ]
            
        elif tool_name == "list_keystore":
            keystore_path = arguments.get("keystore_path")
            storepass = arguments.get("storepass")
            verbose = arguments.get("verbose", False)
            
            if not os.path.exists(keystore_path):
                send_response(id, error={
                    "code": -32602,
                    "message": f"Keystore file does not exist: {keystore_path}"
                })
                return
            
            cmd = [
                "keytool", "-list",
                "-keystore", keystore_path,
                "-storepass", storepass
            ]
            
            if verbose:
                cmd.append("-v")
            
        elif tool_name == "export_certificate":
            keystore_path = arguments.get("keystore_path")
            alias = arguments.get("alias")
            cert_path = arguments.get("cert_path")
            storepass = arguments.get("storepass")
            cert_format = arguments.get("format", "DER")
            
            if not os.path.exists(keystore_path):
                send_response(id, error={
                    "code": -32602,
                    "message": f"Keystore file does not exist: {keystore_path}"
                })
                return
            
            # Create directory for certificate if needed
            cert_dir = os.path.dirname(cert_path)
            if cert_dir and not os.path.exists(cert_dir):
                os.makedirs(cert_dir, exist_ok=True)
            
            cmd = [
                "keytool", "-exportcert",
                "-alias", alias,
                "-keystore", keystore_path,
                "-storepass", storepass,
                "-file", cert_path
            ]
            
            if cert_format.upper() == "PEM":
                cmd.append("-rfc")
                
        elif tool_name == "import_certificate":
            keystore_path = arguments.get("keystore_path")
            alias = arguments.get("alias")
            cert_path = arguments.get("cert_path")
            storepass = arguments.get("storepass")
            noprompt = arguments.get("noprompt", True)
            
            if not os.path.exists(cert_path):
                send_response(id, error={
                    "code": -32602,
                    "message": f"Certificate file does not exist: {cert_path}"
                })
                return
            
            # Validate keystore path
            is_valid, error_msg = validate_keystore_path(keystore_path)
            if not is_valid:
                send_response(id, error={
                    "code": -32602,
                    "message": f"Invalid keystore path: {error_msg}"
                })
                return
            
            cmd = [
                "keytool", "-importcert",
                "-alias", alias,
                "-keystore", keystore_path,
                "-storepass", storepass,
                "-file", cert_path
            ]
            
            if noprompt:
                cmd.append("-noprompt")
                
        elif tool_name == "delete_entry":
            keystore_path = arguments.get("keystore_path")
            alias = arguments.get("alias")
            storepass = arguments.get("storepass")
            
            if not os.path.exists(keystore_path):
                send_response(id, error={
                    "code": -32602,
                    "message": f"Keystore file does not exist: {keystore_path}"
                })
                return
            
            cmd = [
                "keytool", "-delete",
                "-alias", alias,
                "-keystore", keystore_path,
                "-storepass", storepass
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
        
        # Format output with command and results
        output = f"Command: {' '.join(cmd)}\n\n"
        
        if process.stdout:
            output += f"STDOUT:\n{process.stdout}\n"
        if process.stderr:
            output += f"STDERR:\n{process.stderr}\n"
            
        output += f"Exit Code: {process.returncode}"
        
        # Check if operation was successful and add file information
        success = process.returncode == 0
        if success and tool_name in ["generate_keystore", "export_certificate"]:
            if tool_name == "generate_keystore" and os.path.exists(keystore_path):
                output += f"\n\nKeystore created successfully: {keystore_path}"
                output += f"\nKeystore size: {os.path.getsize(keystore_path)} bytes"
            elif tool_name == "export_certificate" and os.path.exists(cert_path):
                output += f"\n\nCertificate exported successfully: {cert_path}"
                output += f"\nCertificate size: {os.path.getsize(cert_path)} bytes"
        
        send_response(id, {
            "content": [
                {
                    "type": "text",
                    "text": output
                }
            ],
            "isError": not success
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
