#!/usr/bin/env python3
"""
MCP Server Diagnostic Tool for GitHub Copilot Workflows

This script helps diagnose and fix issues when GitHub Copilot workflows 
try to start MCP servers, specifically addressing the problems seen in 
workflow runs where the "Start MCP Servers" step fails or times out.
"""

import json
import subprocess
import os
import sys
import time
from pathlib import Path

class MCPServerDiagnostic:
    def __init__(self):
        self.workspace_path = os.environ.get('GITHUB_WORKSPACE', '/github/workspace')
        self.issues_found = []
        self.fixes_applied = []
        
    def log_issue(self, issue, severity="ERROR"):
        """Log an issue found during diagnostics"""
        issue_msg = f"[{severity}] {issue}"
        self.issues_found.append(issue_msg)
        print(issue_msg)
    
    def log_fix(self, fix):
        """Log a fix that was applied"""
        fix_msg = f"[FIX] {fix}"
        self.fixes_applied.append(fix_msg)
        print(fix_msg)
    
    def check_docker_availability(self):
        """Check if Docker is available and can run containers"""
        print("\n🔍 Checking Docker availability...")
        
        try:
            # Check if docker command exists
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                self.log_issue("Docker command not available")
                return False
            
            print(f"✅ Docker version: {result.stdout.strip()}")
            
            # Test basic docker functionality
            result = subprocess.run(['docker', 'run', '--rm', 'hello-world'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                self.log_issue(f"Docker cannot run containers: {result.stderr}")
                return False
            
            print("✅ Docker can run containers")
            return True
            
        except subprocess.TimeoutExpired:
            self.log_issue("Docker command timed out")
            return False
        except FileNotFoundError:
            self.log_issue("Docker command not found")
            return False
        except Exception as e:
            self.log_issue(f"Docker check failed: {e}")
            return False
    
    def check_image_availability(self):
        """Check if the Lanbu Docker image is available"""
        print("\n🔍 Checking Docker image availability...")
        
        image_name = "ghcr.io/millionthodin16/lanbu:latest"
        
        try:
            # Check if image exists locally
            result = subprocess.run(['docker', 'images', '-q', image_name], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.stdout.strip():
                print(f"✅ Image {image_name} is available locally")
                return True
            
            print(f"⚠️  Image {image_name} not found locally, attempting to pull...")
            
            # Try to pull the image
            result = subprocess.run(['docker', 'pull', image_name], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Successfully pulled {image_name}")
                return True
            else:
                self.log_issue(f"Failed to pull image {image_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_issue(f"Timeout while checking/pulling image {image_name}")
            return False
        except Exception as e:
            self.log_issue(f"Image check failed: {e}")
            return False
    
    def check_workspace_setup(self):
        """Check if workspace is properly set up for volume mounting"""
        print("\n🔍 Checking workspace setup...")
        
        # Check current working directory
        cwd = os.getcwd()
        print(f"Current working directory: {cwd}")
        
        # Check if we can access expected files
        expected_files = [
            "mcp-config.sample.json",
            "mcp-config-github-actions.json", 
            "com.Glowbeast.LanBu v0.53.apk",
            "enhanced_mcp_server.py"
        ]
        
        missing_files = []
        for file in expected_files:
            file_path = os.path.join(cwd, file)
            if os.path.exists(file_path):
                print(f"✅ Found: {file}")
            else:
                missing_files.append(file)
                print(f"❌ Missing: {file}")
        
        if missing_files:
            self.log_issue(f"Missing expected files: {missing_files}")
        
        # Test volume mounting
        try:
            test_file = os.path.join(cwd, "test_mount.txt")
            with open(test_file, "w") as f:
                f.write("test")
            
            # Try to access the file through Docker volume mount
            result = subprocess.run([
                'docker', 'run', '--rm', 
                '-v', f'{cwd}:/workspace',
                '-w', '/workspace',
                'alpine:latest', 
                'cat', 'test_mount.txt'
            ], capture_output=True, text=True, timeout=10)
            
            os.remove(test_file)
            
            if result.returncode == 0 and result.stdout.strip() == "test":
                print("✅ Volume mounting works correctly")
                return True
            else:
                self.log_issue("Volume mounting test failed")
                return False
                
        except Exception as e:
            self.log_issue(f"Volume mount test failed: {e}")
            return False
    
    def test_mcp_server_startup(self, server_name, docker_args, timeout=30):
        """Test if a specific MCP server can start up"""
        print(f"\n🔍 Testing {server_name} startup...")
        
        try:
            # Start the server and send a simple request
            cmd = ['docker'] + docker_args
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start up
            time.sleep(2)
            
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.log_issue(f"{server_name} failed to start: {stderr}")
                return False
            
            # For simple servers, send a basic JSON-RPC request
            if server_name in ["apk_signer", "keytool_generator", "downloader"]:
                test_request = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "params": {"args": ["--version"] if server_name != "downloader" else {"url": "test"}}
                }) + '\n'
                
                process.stdin.write(test_request)
                process.stdin.flush()
                
                # Wait for response or timeout
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    if '"jsonrpc"' in stdout:
                        print(f"✅ {server_name} responded correctly")
                        return True
                    else:
                        self.log_issue(f"{server_name} did not provide JSON-RPC response")
                        return False
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.log_issue(f"{server_name} timed out")
                    return False
            else:
                # For complex servers like apktool, just check if they start
                time.sleep(5)
                if process.poll() is None:
                    print(f"✅ {server_name} started successfully")
                    process.terminate()
                    return True
                else:
                    stdout, stderr = process.communicate()
                    self.log_issue(f"{server_name} stopped unexpectedly: {stderr}")
                    return False
                    
        except Exception as e:
            self.log_issue(f"Failed to test {server_name}: {e}")
            return False
    
    def create_optimized_config(self):
        """Create an optimized MCP configuration for GitHub Actions"""
        print("\n🔧 Creating optimized MCP configuration...")
        
        # Simplified config with only the most reliable servers
        optimized_config = {
            "mcpServers": {
                "apk_signer": {
                    "type": "local",
                    "command": "docker",
                    "args": [ 
                        "run", "-i", "--rm", 
                        "-v", "/github/workspace:/workspace", 
                        "-w", "/workspace", 
                        "ghcr.io/millionthodin16/lanbu:latest", 
                        "uber-apk-signer-mcp-server" 
                    ],
                    "tools": ["*"]
                },
                "keytool_generator": {
                    "type": "local",
                    "command": "docker",
                    "args": [ 
                        "run", "-i", "--rm", 
                        "-v", "/github/workspace:/workspace", 
                        "-w", "/workspace", 
                        "ghcr.io/millionthodin16/lanbu:latest", 
                        "keytool-mcp-server" 
                    ],
                    "tools": ["*"]
                },
                "downloader": {
                    "type": "local",
                    "command": "docker",
                    "args": [ 
                        "run", "-i", "--rm", 
                        "-v", "/github/workspace:/workspace", 
                        "-w", "/workspace", 
                        "ghcr.io/millionthodin16/lanbu:latest", 
                        "downloader-mcp-server" 
                    ],
                    "tools": ["*"]
                }
            }
        }
        
        output_file = "mcp-config-optimized.json"
        with open(output_file, 'w') as f:
            json.dump(optimized_config, f, indent=2)
        
        self.log_fix(f"Created optimized configuration: {output_file}")
        return output_file
    
    def run_diagnostics(self):
        """Run complete diagnostic suite"""
        print("🚀 Starting MCP Server Diagnostics for GitHub Copilot Workflows")
        print("=" * 70)
        
        # Basic environment checks
        docker_ok = self.check_docker_availability()
        image_ok = self.check_image_availability() if docker_ok else False
        workspace_ok = self.check_workspace_setup()
        
        # Test individual servers if prerequisites are met
        servers_ok = {}
        if docker_ok and image_ok and workspace_ok:
            test_servers = [
                ("apk_signer", ["run", "-i", "--rm", "-v", f"{os.getcwd()}:/workspace", "-w", "/workspace", "ghcr.io/millionthodin16/lanbu:latest", "uber-apk-signer-mcp-server"]),
                ("keytool_generator", ["run", "-i", "--rm", "-v", f"{os.getcwd()}:/workspace", "-w", "/workspace", "ghcr.io/millionthodin16/lanbu:latest", "keytool-mcp-server"]),
                ("downloader", ["run", "-i", "--rm", "-v", f"{os.getcwd()}:/workspace", "-w", "/workspace", "ghcr.io/millionthodin16/lanbu:latest", "downloader-mcp-server"]),
            ]
            
            for server_name, docker_args in test_servers:
                servers_ok[server_name] = self.test_mcp_server_startup(server_name, docker_args)
        
        # Create optimized config based on results
        if any(servers_ok.values()):
            self.create_optimized_config()
        
        # Generate report
        print("\n" + "=" * 70)
        print("📋 DIAGNOSTIC SUMMARY")
        print("=" * 70)
        
        print(f"Docker Available: {'✅' if docker_ok else '❌'}")
        print(f"Image Available: {'✅' if image_ok else '❌'}")
        print(f"Workspace Setup: {'✅' if workspace_ok else '❌'}")
        
        for server, status in servers_ok.items():
            print(f"{server}: {'✅' if status else '❌'}")
        
        if self.issues_found:
            print(f"\n❌ Issues Found ({len(self.issues_found)}):")
            for issue in self.issues_found:
                print(f"  {issue}")
        
        if self.fixes_applied:
            print(f"\n🔧 Fixes Applied ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                print(f"  {fix}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not docker_ok:
            print("  • Ensure Docker is installed and running in the GitHub Actions environment")
        if not image_ok:
            print("  • Pre-pull the Docker image in GitHub Actions before starting MCP servers")
            print("  • Consider using 'docker pull ghcr.io/millionthodin16/lanbu:latest' in a setup step")
        if not workspace_ok:
            print("  • Verify workspace permissions and volume mounting setup")
        
        working_servers = sum(1 for status in servers_ok.values() if status)
        total_servers = len(servers_ok)
        
        if working_servers == 0:
            print("  • Start with the optimized configuration that includes only basic servers")
        elif working_servers < total_servers:
            print("  • Use the optimized configuration and gradually add more servers")
        else:
            print("  • All servers working! Consider adding back advanced servers like apktool and ghidra")
        
        return {
            "docker_ok": docker_ok,
            "image_ok": image_ok,
            "workspace_ok": workspace_ok,
            "servers_ok": servers_ok,
            "issues": self.issues_found,
            "fixes": self.fixes_applied
        }

def main():
    """Main function"""
    diagnostic = MCPServerDiagnostic()
    results = diagnostic.run_diagnostics()
    
    # Exit with appropriate code
    if results["docker_ok"] and results["image_ok"] and results["workspace_ok"]:
        working_servers = sum(1 for status in results["servers_ok"].values() if status)
        if working_servers > 0:
            print(f"\n🎉 SUCCESS: {working_servers} MCP servers are working correctly!")
            return 0
        else:
            print(f"\n⚠️  WARNING: Environment is ready but no MCP servers are working")
            return 1
    else:
        print(f"\n❌ FAILURE: Critical issues prevent MCP servers from working")
        return 1

if __name__ == "__main__":
    sys.exit(main())