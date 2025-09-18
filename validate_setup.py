#!/usr/bin/env python3
"""
Quick validation script for MCP servers and APK file setup.
Run this to verify everything is working correctly.
"""

import json
import subprocess
import sys
import os

def run_command(command, timeout=10):
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_docker_image():
    """Test if the Docker image is available"""
    print("🔍 Checking Docker image availability...")
    success, stdout, stderr = run_command("docker images ghcr.io/millionthodin16/lanbu:latest")
    
    if success and "ghcr.io/millionthodin16/lanbu" in stdout:
        print("✅ Docker image is available locally")
        return True
    else:
        print("⚠️  Docker image not found locally, attempting to pull...")
        success, stdout, stderr = run_command("docker pull ghcr.io/millionthodin16/lanbu:latest", timeout=120)
        if success:
            print("✅ Docker image pulled successfully")
            return True
        else:
            print("❌ Failed to pull Docker image")
            print(f"Error: {stderr}")
            return False

def test_apk_file():
    """Test if APK file exists"""
    print("🔍 Checking APK file...")
    apk_file = "com.Glowbeast.LanBu v0.53.apk"
    
    if os.path.exists(apk_file):
        size = os.path.getsize(apk_file)
        print(f"✅ APK file found: {apk_file} ({size:,} bytes)")
        return True
    else:
        print(f"❌ APK file not found: {apk_file}")
        print("Please ensure the APK file is in the current directory")
        return False

def test_simple_mcp_server(name, command):
    """Test a simple MCP server"""
    print(f"🔍 Testing {name}...")
    
    test_cmd = f"echo '{{\"jsonrpc\": \"2.0\", \"id\": 1, \"params\": {{\"args\": [\"--version\"]}}}}' | docker run -i --rm -v $(pwd):/workspace -w /workspace ghcr.io/millionthodin16/lanbu:latest {command}"
    
    success, stdout, stderr = run_command(test_cmd, timeout=15)
    
    if success and "jsonrpc" in stdout:
        print(f"✅ {name} is working")
        return True
    else:
        print(f"❌ {name} failed")
        if stderr:
            print(f"Error: {stderr[:200]}...")
        return False

def test_mcp_config():
    """Test if MCP configuration file exists"""
    print("🔍 Checking MCP configuration...")
    
    if os.path.exists("mcp-config.sample.json"):
        try:
            with open("mcp-config.sample.json", 'r') as f:
                config = json.load(f)
            
            servers = config.get("mcpServers", {})
            print(f"✅ MCP configuration found with {len(servers)} servers configured")
            return True
        except json.JSONDecodeError:
            print("❌ MCP configuration file is invalid JSON")
            return False
    else:
        print("❌ MCP configuration file (mcp-config.sample.json) not found")
        return False

def main():
    """Run quick validation checks"""
    print("🚀 Quick MCP Server Validation")
    print("=" * 40)
    
    checks = [
        ("Docker Image", test_docker_image),
        ("APK File", test_apk_file),
        ("MCP Configuration", test_mcp_config),
        ("Uber APK Signer Server", lambda: test_simple_mcp_server("uber-apk-signer-mcp-server", "uber-apk-signer-mcp-server")),
        ("Keytool Server", lambda: test_simple_mcp_server("keytool-mcp-server", "keytool-mcp-server")),
    ]
    
    results = []
    for name, test_func in checks:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("📋 VALIDATION SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All validation checks passed!")
        print("Your MCP server setup is ready to use.")
        print("\nNext steps:")
        print("1. Configure your MCP client with mcp-config.sample.json")
        print("2. Use the MCP servers for APK analysis")
        print("3. Refer to MCP_SETUP.md for usage examples")
        return 0
    else:
        print(f"\n⚠️  {total - passed} validation checks failed.")
        print("Please resolve the issues above before using the MCP servers.")
        print("Refer to MCP_SETUP.md for troubleshooting guidance.")
        return 1

if __name__ == "__main__":
    sys.exit(main())