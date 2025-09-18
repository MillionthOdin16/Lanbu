#!/usr/bin/env python3
"""
Enhanced MCP server wrapper with improved error handling and logging.
This provides better diagnostics for MCP server issues.
"""

import json
import subprocess
import sys
import os
import logging
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp-server-wrapper')

def send_response(request_id: Optional[str], result: Dict[str, Any]) -> None:
    """Send a JSON-RPC response with error handling"""
    try:
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        print(json.dumps(response) + '\n', flush=True)
    except Exception as e:
        logger.error(f"Failed to send response: {e}")
        error_response = {
            "jsonrpc": "2.0", 
            "id": request_id,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }
        print(json.dumps(error_response) + '\n', flush=True)

def send_error(request_id: Optional[str], code: int, message: str, data: Optional[str] = None) -> None:
    """Send a JSON-RPC error response"""
    error_response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message
        }
    }
    if data:
        error_response["error"]["data"] = data
    
    print(json.dumps(error_response) + '\n', flush=True)

def validate_request(request: Dict[str, Any]) -> bool:
    """Validate a JSON-RPC request"""
    required_fields = ["jsonrpc", "id"]
    
    for field in required_fields:
        if field not in request:
            logger.error(f"Missing required field: {field}")
            return False
    
    if request.get("jsonrpc") != "2.0":
        logger.error(f"Invalid JSON-RPC version: {request.get('jsonrpc')}")
        return False
    
    return True

def execute_command_with_diagnostics(command: list, timeout: int = 30) -> Dict[str, Any]:
    """Execute a command with comprehensive diagnostics"""
    start_time = time.time()
    
    try:
        logger.info(f"Executing command: {' '.join(command)}")
        
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        execution_time = time.time() - start_time
        
        result = {
            "output": f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}",
            "exitCode": process.returncode,
            "executionTime": round(execution_time, 3),
            "command": ' '.join(command)
        }
        
        if process.returncode != 0:
            logger.warning(f"Command failed with exit code {process.returncode}")
            logger.warning(f"STDERR: {process.stderr}")
        else:
            logger.info(f"Command completed successfully in {execution_time:.3f}s")
        
        return result
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        logger.error(f"Command timed out after {timeout}s")
        return {
            "output": f"STDOUT:\n\nSTDERR:\nCommand timed out after {timeout} seconds",
            "exitCode": -1,
            "executionTime": round(execution_time, 3),
            "command": ' '.join(command),
            "error": "timeout"
        }
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Command execution failed: {e}")
        return {
            "output": f"STDOUT:\n\nSTDERR:\nExecution error: {str(e)}",
            "exitCode": -2,
            "executionTime": round(execution_time, 3),
            "command": ' '.join(command),
            "error": str(e)
        }

def enhanced_uber_apk_signer_server():
    """Enhanced uber-apk-signer MCP server with better error handling"""
    uber_apk_signer_path = "/usr/local/bin/uber-apk-signer.jar"
    
    # Check if the JAR file exists
    if not os.path.exists(uber_apk_signer_path):
        logger.error(f"uber-apk-signer.jar not found at {uber_apk_signer_path}")
        send_error(None, -32000, "uber-apk-signer.jar not found", uber_apk_signer_path)
        return
    
    logger.info("Enhanced uber-apk-signer MCP server starting...")
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            if not line.strip():
                continue
                
            try:
                request = json.loads(line.strip())
                logger.debug(f"Received request: {request}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                send_error(None, -32700, "Parse error", str(e))
                continue
            
            if not validate_request(request):
                send_error(request.get("id"), -32602, "Invalid request")
                continue
            
            req_id = request.get("id")
            params = request.get("params", {})
            command_args = params.get("args", [])
            
            if not isinstance(command_args, list):
                send_error(req_id, -32602, "Invalid parameters: 'args' must be a list")
                continue
            
            # Execute uber-apk-signer with the provided arguments
            cmd = ["java", "-jar", uber_apk_signer_path] + command_args
            result = execute_command_with_diagnostics(cmd)
            
            send_response(req_id, result)
            
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            send_error(None, -32603, "Internal error", str(e))

def enhanced_keytool_server():
    """Enhanced keytool MCP server with better error handling"""
    logger.info("Enhanced keytool MCP server starting...")
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            if not line.strip():
                continue
                
            try:
                request = json.loads(line.strip())
                logger.debug(f"Received request: {request}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                send_error(None, -32700, "Parse error", str(e))
                continue
            
            if not validate_request(request):
                send_error(request.get("id"), -32602, "Invalid request")
                continue
            
            req_id = request.get("id")
            params = request.get("params", {})
            command_args = params.get("args", [])
            
            if not isinstance(command_args, list):
                send_error(req_id, -32602, "Invalid parameters: 'args' must be a list")
                continue
            
            # Execute keytool with the provided arguments
            cmd = ["keytool"] + command_args
            result = execute_command_with_diagnostics(cmd)
            
            send_response(req_id, result)
            
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            send_error(None, -32603, "Internal error", str(e))

def enhanced_downloader_server():
    """Enhanced downloader MCP server with better error handling"""
    logger.info("Enhanced downloader MCP server starting...")
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            if not line.strip():
                continue
                
            try:
                request = json.loads(line.strip())
                logger.debug(f"Received request: {request}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                send_error(None, -32700, "Parse error", str(e))
                continue
            
            if not validate_request(request):
                send_error(request.get("id"), -32602, "Invalid request")
                continue
            
            req_id = request.get("id")
            params = request.get("params", {})
            url = params.get("url")
            
            if not url:
                send_error(req_id, -32602, "Invalid parameters: 'url' is required")
                continue
            
            try:
                import requests
                from urllib.parse import urlparse
                
                # Default to saving in the current directory (/workspace)
                output_dir = os.getcwd()
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    filename = "downloaded_file"
                
                output_path = os.path.join(output_dir, filename)
                
                logger.info(f"Downloading {url} to {output_path}")
                start_time = time.time()
                
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                execution_time = time.time() - start_time
                file_size = os.path.getsize(output_path)
                
                result = {
                    "status": "success",
                    "message": f"File downloaded successfully to {output_path}",
                    "url": url,
                    "outputPath": output_path,
                    "fileSize": file_size,
                    "executionTime": round(execution_time, 3)
                }
                
                logger.info(f"Download completed: {file_size} bytes in {execution_time:.3f}s")
                send_response(req_id, result)
                
            except Exception as e:
                logger.error(f"Download failed: {e}")
                send_response(req_id, {
                    "status": "error",
                    "message": str(e),
                    "url": url
                })
            
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            send_error(None, -32603, "Internal error", str(e))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        server_type = sys.argv[1]
        if server_type == "uber-apk-signer":
            enhanced_uber_apk_signer_server()
        elif server_type == "keytool":
            enhanced_keytool_server()
        elif server_type == "downloader":
            enhanced_downloader_server()
        else:
            print(f"Unknown server type: {server_type}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: enhanced_mcp_server.py <server_type>", file=sys.stderr)
        print("Server types: uber-apk-signer, keytool, downloader", file=sys.stderr)
        sys.exit(1)