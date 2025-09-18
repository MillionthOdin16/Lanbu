#!/usr/bin/env python3
"""
Enhanced MCP Server Feature Test - demonstrates all the new capabilities.
"""

import json
import subprocess
import tempfile
import os
import sys

def execute_mcp_command(server_script, method, params=None, timeout=30):
    """Execute a single MCP command and return the result."""
    commands = [
        '{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {"protocolVersion": "2024-11-05"}}',
        '{"jsonrpc": "2.0", "method": "initialized"}',
    ]
    
    if method != "initialize":
        command = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 2,
            "params": params or {}
        }
        commands.append(json.dumps(command))
    
    input_data = "\n".join(commands) + "\n"
    
    try:
        result = subprocess.run(
            [sys.executable, str(server_script)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Parse the last JSON response
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:  # Should have initialize response and command response
            return json.loads(lines[-1])
        return None
        
    except subprocess.TimeoutExpired:
        print(f"    ⚠️  Command timed out after {timeout}s")
        return None
    except Exception as e:
        print(f"    ❌ Exception: {e}")
        return None

def test_enhanced_features():
    """Test all enhanced MCP server features."""
    print("🚀 Enhanced MCP Server Feature Test")
    print("=" * 60)
    
    repo_dir = "/home/runner/work/Lanbu/Lanbu"
    apk_file = f"{repo_dir}/com.Glowbeast.LanBu v0.53.apk"
    
    print("📱 Testing Enhanced Features with Real APK")
    print(f"   APK: {os.path.basename(apk_file)}")
    print()
    
    # Test 1: Tool Availability Checks
    print("1️⃣ Tool Availability Checks:")
    
    # Check keytool availability
    response = execute_mcp_command(
        f"{repo_dir}/keytool-mcp-server.py",
        "tools/call",
        {"name": "check_tool_availability", "arguments": {}}
    )
    
    if response and "result" in response:
        content = response["result"]["content"][0]["text"]
        print("   ✅ Keytool availability check successful")
        print(f"   📋 {content.split(':', 1)[1].strip()}")
    else:
        print("   ❌ Keytool availability check failed")
    
    # Check uber-apk-signer availability
    response = execute_mcp_command(
        f"{repo_dir}/uber-apk-signer-mcp-server.py",
        "tools/call",
        {"name": "check_tool_availability", "arguments": {}}
    )
    
    if response and "result" in response:
        content = response["result"]["content"][0]["text"]
        print("   ✅ Uber APK Signer availability check successful")
        print(f"   📋 {content.split(':', 1)[1].strip()}")
    else:
        print("   ❌ Uber APK Signer availability check failed")
    
    print()
    
    # Test 2: APK Information Extraction
    print("2️⃣ APK Information Extraction:")
    
    response = execute_mcp_command(
        f"{repo_dir}/uber-apk-signer-mcp-server.py",
        "tools/call",
        {"name": "get_apk_info", "arguments": {"apk_path": apk_file}}
    )
    
    if response and "result" in response:
        content = response["result"]["content"][0]["text"]
        print("   ✅ APK info extraction successful")
        
        # Extract hash for later use
        import re
        hash_match = re.search(r'"sha256": "([a-f0-9]{64})"', content)
        apk_hash = hash_match.group(1) if hash_match else None
        print(f"   📋 APK SHA256: {apk_hash}")
    else:
        print("   ❌ APK info extraction failed")
        apk_hash = None
    
    print()
    
    # Test 3: File Integrity Verification
    print("3️⃣ File Integrity Verification:")
    
    if apk_hash:
        response = execute_mcp_command(
            f"{repo_dir}/downloader.py",
            "tools/call",
            {
                "name": "verify_file_integrity",
                "arguments": {
                    "file_path": apk_file,
                    "expected_hash": apk_hash
                }
            }
        )
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            if "integrity_verified\": true" in content:
                print("   ✅ File integrity verification successful")
                print("   🔒 APK integrity confirmed")
            else:
                print("   ❌ File integrity verification failed")
        else:
            print("   ❌ File integrity verification request failed")
    else:
        print("   ⚠️  Skipped - no hash available")
    
    print()
    
    # Test 4: Enhanced Download with Integrity Checking
    print("4️⃣ Enhanced Download with Integrity Checking:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        download_path = os.path.join(temp_dir, "test_download.json")
        
        response = execute_mcp_command(
            f"{repo_dir}/downloader.py",
            "tools/call",
            {
                "name": "download_file",
                "arguments": {
                    "url": "https://httpbin.org/json",
                    "output_path": download_path,
                    "max_size": 1024,  # 1KB limit for test
                    "verify_ssl": True
                }
            }
        )
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            if "downloaded successfully" in content.lower():
                print("   ✅ Enhanced download successful")
                
                # Verify file was created
                if os.path.exists(download_path):
                    print(f"   📁 File created: {os.path.getsize(download_path)} bytes")
                else:
                    print("   ❌ File not created")
            else:
                print("   ❌ Enhanced download failed")
        else:
            print("   ❌ Enhanced download request failed")
    
    print()
    
    # Test 5: Advanced Keystore Operations
    print("5️⃣ Advanced Keystore Operations:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        keystore_path = os.path.join(temp_dir, "enhanced_test.keystore")
        cert_path = os.path.join(temp_dir, "test_cert.der")
        
        # Generate keystore with custom parameters
        response = execute_mcp_command(
            f"{repo_dir}/keytool-mcp-server.py",
            "tools/call",
            {
                "name": "generate_keystore",
                "arguments": {
                    "keystore_path": keystore_path,
                    "alias": "enhanced_test_key",
                    "dname": "CN=Enhanced Test, O=MCP Test Suite, L=Test City, ST=Test State, C=US",
                    "keypass": "keypass123",
                    "storepass": "storepass123",
                    "validity": "1095",  # 3 years
                    "keyalg": "RSA",
                    "keysize": "2048"
                }
            }
        )
        
        if response and "result" in response and not response["result"].get("isError", True):
            print("   ✅ Enhanced keystore generation successful")
            
            # Export certificate
            export_response = execute_mcp_command(
                f"{repo_dir}/keytool-mcp-server.py",
                "tools/call",
                {
                    "name": "export_certificate",
                    "arguments": {
                        "keystore_path": keystore_path,
                        "alias": "enhanced_test_key",
                        "cert_path": cert_path,
                        "storepass": "storepass123",
                        "format": "DER"
                    }
                }
            )
            
            if export_response and "result" in export_response and not export_response["result"].get("isError", True):
                print("   ✅ Certificate export successful")
                
                if os.path.exists(cert_path):
                    print(f"   📜 Certificate created: {os.path.getsize(cert_path)} bytes")
                else:
                    print("   ❌ Certificate file not created")
            else:
                print("   ❌ Certificate export failed")
        else:
            print("   ❌ Enhanced keystore generation failed")
    
    print()
    
    # Test 6: Enhanced URL Information
    print("6️⃣ Enhanced URL Information:")
    
    response = execute_mcp_command(
        f"{repo_dir}/downloader.py",
        "tools/call",
        {
            "name": "get_url_info",
            "arguments": {
                "url": "https://httpbin.org/redirect/2",
                "follow_redirects": True
            }
        }
    )
    
    if response and "result" in response:
        content = response["result"]["content"][0]["text"]
        if "final_url" in content and "redirected" in content:
            print("   ✅ Enhanced URL info with redirect tracking successful")
            
            # Check if redirect was detected
            if '"redirected": true' in content:
                print("   🔄 Redirect detected and followed")
            else:
                print("   ➡️  No redirect detected")
        else:
            print("   ❌ Enhanced URL info missing expected fields")
    else:
        print("   ❌ Enhanced URL info request failed")
    
    print()
    print("=" * 60)
    print("🎯 Enhanced Feature Test Complete!")
    print("All enhanced MCP server features have been tested.")
    print("The servers now provide:")
    print("  • Tool availability validation")
    print("  • File integrity verification with SHA256")
    print("  • APK metadata extraction")
    print("  • Enhanced download with size limits and SSL verification")
    print("  • Advanced keystore operations with custom parameters")
    print("  • URL redirect tracking and detailed metadata")
    print("=" * 60)

if __name__ == "__main__":
    test_enhanced_features()