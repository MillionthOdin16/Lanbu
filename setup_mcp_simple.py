#!/usr/bin/env python3
"""
Simple MCP Server Setup Script for GitHub Copilot Workflows

This addresses the specific issues found in GitHub Copilot workflow runs.
"""

import json
import subprocess
import os
import sys
import time

def run_command(cmd, timeout=30):
    """Run a command with timeout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def log(message):
    """Log with timestamp"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def test_mcp_server(server_name, docker_cmd):
    """Test an individual MCP server"""
    log(f"Testing {server_name}...")
    
    # Simple test request
    test_request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "params": {"args": ["--version"]}
    })
    
    full_cmd = f"echo '{test_request}' | {docker_cmd}"
    success, stdout, stderr = run_command(full_cmd, timeout=15)
    
    if success and '"jsonrpc"' in stdout:
        log(f"✅ {server_name} working")
        return True
    else:
        log(f"❌ {server_name} failed: {stderr}")
        return False

def main():
    """Main setup function"""
    log("🚀 Setting up MCP servers for GitHub Copilot workflow...")
    
    workspace = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
    log(f"📍 Workspace: {workspace}")
    
    # Pre-flight checks
    log("🔍 Checking Docker...")
    success, stdout, stderr = run_command("docker --version")
    if not success:
        log("❌ Docker not available")
        return 1
    log(f"✅ {stdout.strip()}")
    
    # Pull Docker image
    log("📥 Pulling Docker image...")
    image = "ghcr.io/millionthodin16/lanbu:latest"
    success, stdout, stderr = run_command(f"docker pull {image}", timeout=300)
    if not success:
        log(f"❌ Failed to pull image: {stderr}")
        return 1
    log("✅ Image pulled successfully")
    
    # Test volume mounting
    log("🧪 Testing volume mounting...")
    test_cmd = f"echo 'test' > /tmp/mount_test && docker run --rm -v /tmp:/test {image} cat /test/mount_test && rm /tmp/mount_test"
    success, stdout, stderr = run_command(test_cmd)
    if not success or "test" not in stdout:
        log("❌ Volume mounting failed")
        return 1
    log("✅ Volume mounting works")
    
    # Test MCP servers
    servers = {
        "apk_signer": f"docker run -i --rm -v {workspace}:/workspace -w /workspace {image} python3 uber-apk-signer-mcp-server.py",
        "keytool_generator": f"docker run -i --rm -v {workspace}:/workspace -w /workspace {image} python3 keytool-mcp-server.py",
        "downloader": f"docker run -i --rm -v {workspace}:/workspace -w /workspace {image} python3 downloader.py",
    }
    
    working_servers = {}
    for name, cmd in servers.items():
        working_servers[name] = test_mcp_server(name, cmd)
    
    # Create validated configuration
    log("📝 Creating validated MCP configuration...")
    
    config = {"mcpServers": {}}
    
    if working_servers.get("apk_signer"):
        config["mcpServers"]["apk_signer"] = {
            "type": "local",
            "command": "docker",
            "args": [
                "run", "-i", "--rm",
                "-v", "/github/workspace:/workspace",
                "-w", "/workspace",
                "ghcr.io/millionthodin16/lanbu:latest",
                "python3", "uber-apk-signer-mcp-server.py"
            ],
            "tools": ["*"]
        }
    
    if working_servers.get("keytool_generator"):
        config["mcpServers"]["keytool_generator"] = {
            "type": "local",
            "command": "docker",
            "args": [
                "run", "-i", "--rm",
                "-v", "/github/workspace:/workspace",
                "-w", "/workspace",
                "ghcr.io/millionthodin16/lanbu:latest",
                "python3", "keytool-mcp-server.py"
            ],
            "tools": ["*"]
        }
    
    if working_servers.get("downloader"):
        config["mcpServers"]["downloader"] = {
            "type": "local",
            "command": "docker",
            "args": [
                "run", "-i", "--rm",
                "-v", "/github/workspace:/workspace",
                "-w", "/workspace",
                "ghcr.io/millionthodin16/lanbu:latest",
                "python3", "downloader.py"
            ],
            "tools": ["*"]
        }
    
    # Write configuration
    config_file = os.path.join(workspace, "mcp-config-validated.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    working_count = sum(working_servers.values())
    log(f"📊 SETUP SUMMARY: {working_count}/{len(servers)} servers working")
    
    for name, status in working_servers.items():
        log(f"{'✅' if status else '❌'} {name}")
    
    if working_count > 0:
        log(f"✅ Created validated config: {config_file}")
        log("🎉 SUCCESS: MCP servers ready for GitHub Copilot")
        return 0
    else:
        log("❌ FAILURE: No working MCP servers")
        return 1

if __name__ == "__main__":
    sys.exit(main())