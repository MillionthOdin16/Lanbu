#!/usr/bin/env python3
import sys
import json
import requests
import os
import hashlib
import mimetypes
from urllib.parse import urlparse
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

def handle_initialize(id, params):
    """Handle MCP initialize request."""
    send_response(id, {
        "protocolVersion": MCP_VERSION,
        "capabilities": {
            "tools": {
                "listChanged": False
            }
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
                "description": "Download a file from a URL with integrity verification",
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
                        },
                        "verify_ssl": {
                            "type": "boolean",
                            "description": "Whether to verify SSL certificates (default: true)"
                        },
                        "max_size": {
                            "type": "integer",
                            "description": "Maximum file size in bytes (default: 100MB)"
                        },
                        "expected_hash": {
                            "type": "string",
                            "description": "Expected SHA256 hash for verification (optional)"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "get_url_info",
                "description": "Get detailed information about a URL without downloading",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to get information about"
                        },
                        "follow_redirects": {
                            "type": "boolean",
                            "description": "Whether to follow redirects (default: true)"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "verify_file_integrity",
                "description": "Verify the integrity of a downloaded file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to verify"
                        },
                        "expected_hash": {
                            "type": "string",
                            "description": "Expected SHA256 hash"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]
    })

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        return None

def validate_url(url):
    """Validate URL format and scheme."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format"
        if parsed.scheme not in ['http', 'https']:
            return False, "Only HTTP and HTTPS URLs are supported"
        return True, None
    except Exception as e:
        return False, str(e)

def handle_tools_call(id, params):
    """Handle tools/call request."""
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "verify_file_integrity":
            file_path = arguments.get("file_path")
            expected_hash = arguments.get("expected_hash")
            
            if not file_path:
                send_response(id, error={
                    "code": -32602,
                    "message": "file_path parameter is required"
                })
                return
            
            if not os.path.exists(file_path):
                send_response(id, error={
                    "code": -32602,
                    "message": f"File does not exist: {file_path}"
                })
                return
            
            actual_hash = calculate_file_hash(file_path)
            if actual_hash is None:
                send_response(id, error={
                    "code": -32000,
                    "message": "Failed to calculate file hash"
                })
                return
            
            file_size = os.path.getsize(file_path)
            
            verification_result = {
                "file_path": file_path,
                "file_size": file_size,
                "sha256_hash": actual_hash,
                "expected_hash": expected_hash,
                "integrity_verified": actual_hash == expected_hash if expected_hash else None
            }
            
            send_response(id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"File Integrity Verification:\n{json.dumps(verification_result, indent=2)}"
                    }
                ],
                "isError": False
            })
            return

        elif tool_name == "download_file":
            url = arguments.get("url")
            output_path = arguments.get("output_path")
            custom_filename = arguments.get("filename")
            verify_ssl = arguments.get("verify_ssl", True)
            max_size = arguments.get("max_size", 100 * 1024 * 1024)  # 100MB default
            expected_hash = arguments.get("expected_hash")

            if not url:
                send_response(id, error={
                    "code": -32602,
                    "message": "URL parameter is required"
                })
                return
            
            # Validate URL
            is_valid, error_msg = validate_url(url)
            if not is_valid:
                send_response(id, error={
                    "code": -32602,
                    "message": error_msg
                })
                return

            # Determine output path
            if output_path:
                final_path = output_path
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(final_path), exist_ok=True)
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

            # Download the file with progress tracking
            session = requests.Session()
            session.verify = verify_ssl
            
            with session.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()
                
                # Check content length
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > max_size:
                    send_response(id, error={
                        "code": -32000,
                        "message": f"File too large: {content_length} bytes (max: {max_size})"
                    })
                    return
                
                downloaded_size = 0
                hash_sha256 = hashlib.sha256()
                
                with open(final_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            downloaded_size += len(chunk)
                            if downloaded_size > max_size:
                                os.remove(final_path)
                                send_response(id, error={
                                    "code": -32000,
                                    "message": f"File too large: {downloaded_size} bytes (max: {max_size})"
                                })
                                return
                            f.write(chunk)
                            hash_sha256.update(chunk)
            
            file_size = os.path.getsize(final_path)
            file_hash = hash_sha256.hexdigest()
            
            # Verify hash if provided
            hash_verified = None
            if expected_hash:
                hash_verified = file_hash == expected_hash.lower()
                if not hash_verified:
                    send_response(id, error={
                        "code": -32000,
                        "message": f"Hash verification failed. Expected: {expected_hash}, Got: {file_hash}"
                    })
                    return
            
            # Get MIME type
            mime_type = mimetypes.guess_type(final_path)[0] or response.headers.get('content-type', 'unknown')
            
            result = {
                "downloaded_file": final_path,
                "file_size": file_size,
                "sha256_hash": file_hash,
                "content_type": mime_type,
                "hash_verified": hash_verified,
                "url": url
            }
            
            send_response(id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"File downloaded successfully!\n{json.dumps(result, indent=2)}"
                    }
                ],
                "isError": False
            })

        elif tool_name == "get_url_info":
            url = arguments.get("url")
            follow_redirects = arguments.get("follow_redirects", True)

            if not url:
                send_response(id, error={
                    "code": -32602,
                    "message": "URL parameter is required"
                })
                return
            
            # Validate URL
            is_valid, error_msg = validate_url(url)
            if not is_valid:
                send_response(id, error={
                    "code": -32602,
                    "message": error_msg
                })
                return

            # Get URL information with HEAD request
            session = requests.Session()
            response = session.head(url, allow_redirects=follow_redirects, timeout=10)
            response.raise_for_status()
            
            # Get final URL after redirects
            final_url = response.url
            
            info = {
                "original_url": url,
                "final_url": final_url,
                "redirected": url != final_url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_length": response.headers.get('content-length', 'unknown'),
                "content_type": response.headers.get('content-type', 'unknown'),
                "server": response.headers.get('server', 'unknown'),
                "last_modified": response.headers.get('last-modified', 'unknown')
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
            "message": f"Network error: {str(e)}"
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
