#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import hashlib
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

def validate_apk_file(apk_path):
    """Validate that the APK file exists and is a valid ZIP file."""
    if not os.path.exists(apk_path):
        return False, f"APK file does not exist: {apk_path}"
    
    if not os.path.isfile(apk_path):
        return False, f"Path is not a file: {apk_path}"
    
    # Check if it's a ZIP file (APK is a ZIP)
    try:
        with open(apk_path, 'rb') as f:
            header = f.read(4)
            if header[:2] != b'PK':
                return False, f"File does not appear to be a ZIP/APK file: {apk_path}"
    except Exception as e:
        return False, f"Cannot read file: {e}"
    
    return True, None

def get_apk_info(apk_path):
    """Get basic information about the APK file."""
    try:
        stat = os.stat(apk_path)
        
        # Calculate file hash for integrity checking
        with open(apk_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        return {
            "path": apk_path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "sha256": file_hash
        }
    except Exception as e:
        return {"path": apk_path, "error": str(e)}

def check_uber_apk_signer_availability():
    """Check if uber-apk-signer.jar is available."""
    uber_apk_signer_path = "/usr/local/bin/uber-apk-signer.jar"
    
    if os.path.exists(uber_apk_signer_path):
        return True, uber_apk_signer_path
    
    # Try alternative locations
    alternative_paths = [
        "/opt/uber-apk-signer.jar",
        "/usr/share/uber-apk-signer/uber-apk-signer.jar",
        "./uber-apk-signer.jar"
    ]
    
    for path in alternative_paths:
        if os.path.exists(path):
            return True, path
    
    return False, uber_apk_signer_path

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
                        "apk_path": {
                            "type": "string",
                            "description": "Path to the APK file to sign"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Output path for the signed APK (optional)"
                        },
                        "keystore_path": {
                            "type": "string",
                            "description": "Path to keystore file (optional, will use debug key if not provided)"
                        },
                        "keystore_pass": {
                            "type": "string",
                            "description": "Keystore password (optional)"
                        },
                        "key_alias": {
                            "type": "string", 
                            "description": "Key alias in keystore (optional)"
                        },
                        "key_pass": {
                            "type": "string",
                            "description": "Key password (optional)"
                        }
                    },
                    "required": ["apk_path"]
                }
            },
            {
                "name": "verify_apk",
                "description": "Verify APK signature using uber-apk-signer",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "apk_path": {
                            "type": "string",
                            "description": "Path to the APK file to verify"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed verification information"
                        }
                    },
                    "required": ["apk_path"]
                }
            },
            {
                "name": "get_apk_info",
                "description": "Get information about an APK file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "apk_path": {
                            "type": "string",
                            "description": "Path to the APK file"
                        }
                    },
                    "required": ["apk_path"]
                }
            },
            {
                "name": "check_tool_availability",
                "description": "Check if uber-apk-signer tool is available",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
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
            # Check if uber-apk-signer is available
            available, path = check_uber_apk_signer_availability()
            
            result = {
                "available": available,
                "path": path,
                "java_available": subprocess.run(["which", "java"], capture_output=True).returncode == 0
            }
            
            send_response(id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool Availability Check:\n{json.dumps(result, indent=2)}"
                    }
                ],
                "isError": False
            })
            return

        elif tool_name == "get_apk_info":
            apk_path = arguments.get("apk_path")
            
            if not apk_path:
                send_response(id, error={
                    "code": -32602,
                    "message": "apk_path is required"
                })
                return
            
            # Validate APK file
            is_valid, error_msg = validate_apk_file(apk_path)
            if not is_valid:
                send_response(id, error={
                    "code": -32602,
                    "message": error_msg
                })
                return
            
            # Get APK information
            apk_info = get_apk_info(apk_path)
            
            send_response(id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"APK Information:\n{json.dumps(apk_info, indent=2)}"
                    }
                ],
                "isError": False
            })
            return

        elif tool_name == "sign_apk":
            apk_path = arguments.get("apk_path")
            output_path = arguments.get("output_path")
            keystore_path = arguments.get("keystore_path")
            keystore_pass = arguments.get("keystore_pass")
            key_alias = arguments.get("key_alias")
            key_pass = arguments.get("key_pass")
            
            if not apk_path:
                send_response(id, error={
                    "code": -32602,
                    "message": "apk_path is required"
                })
                return
            
            # Validate APK file
            is_valid, error_msg = validate_apk_file(apk_path)
            if not is_valid:
                send_response(id, error={
                    "code": -32602,
                    "message": error_msg
                })
                return
            
            # Check tool availability
            available, uber_apk_signer_path = check_uber_apk_signer_availability()
            if not available:
                send_response(id, error={
                    "code": -32000,
                    "message": f"uber-apk-signer.jar not found. Checked: {uber_apk_signer_path}"
                })
                return
                
            # Build command for signing
            cmd = ["java", "-jar", uber_apk_signer_path, "--apks", apk_path]
            
            if output_path:
                cmd.extend(["--out", output_path])
            if keystore_path:
                cmd.extend(["--ks", keystore_path])
                if keystore_pass:
                    cmd.extend(["--ksPass", keystore_pass])
                if key_alias:
                    cmd.extend(["--ksAlias", key_alias])
                if key_pass:
                    cmd.extend(["--ksKeyPass", key_pass])
                    
        elif tool_name == "verify_apk":
            apk_path = arguments.get("apk_path")
            verbose = arguments.get("verbose", False)
            
            if not apk_path:
                send_response(id, error={
                    "code": -32602,
                    "message": "apk_path is required"
                })
                return
            
            # Validate APK file
            is_valid, error_msg = validate_apk_file(apk_path)
            if not is_valid:
                send_response(id, error={
                    "code": -32602,
                    "message": error_msg
                })
                return
            
            # Check tool availability
            available, uber_apk_signer_path = check_uber_apk_signer_availability()
            if not available:
                send_response(id, error={
                    "code": -32000,
                    "message": f"uber-apk-signer.jar not found. Checked: {uber_apk_signer_path}"
                })
                return
                
            # Build command for verification
            cmd = ["java", "-jar", uber_apk_signer_path, "--verify", "--apks", apk_path]
            if verbose:
                cmd.append("--verbose")
            
        else:
            send_response(id, error={
                "code": -32601,
                "message": f"Unknown tool: {tool_name}"
            })
            return

        # Execute uber-apk-signer command
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=120  # Increased timeout for large APK files
        )
        
        # Get APK info for context
        apk_info = get_apk_info(apk_path) if apk_path else {}
        
        output = f"Command: {' '.join(cmd)}\n\n"
        output += f"APK Info: {json.dumps(apk_info, indent=2)}\n\n"
        output += f"STDOUT:\n{process.stdout}\n"
        output += f"STDERR:\n{process.stderr}\n"
        output += f"Exit Code: {process.returncode}"
        
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
            "message": "Command timed out after 120 seconds"
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