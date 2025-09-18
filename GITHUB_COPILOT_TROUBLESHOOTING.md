# GitHub Copilot MCP Server Troubleshooting Guide

This guide addresses the specific issues found in GitHub Copilot workflow runs where MCP servers fail to start or time out.

## Issues Identified from Workflow Logs

### 1. **"Start MCP Servers" Step Cancellation/Timeout**

**Symptoms:**
- Workflow step "Start MCP Servers" shows as "cancelled" 
- Log shows "MCP Tool server started successfully" followed by "##[error]The operation was canceled."
- Timeout after ~53 seconds during server startup

**Root Causes:**
1. **Docker Image Pull Delays**: GitHub Copilot workflows don't pre-pull the Docker image, causing timeouts during first-time pulls
2. **Volume Mount Issues**: Incorrect workspace path mapping between GitHub Actions environment and Docker containers
3. **Server Startup Timeouts**: Complex MCP servers like apktool-mcp-server take longer to initialize than the workflow timeout allows
4. **Resource Constraints**: GitHub Actions runners may have limited resources affecting Docker container startup

### 2. **Configuration Path Issues**

**Symptoms:**
- Enhanced servers fail to start when referencing `/workspace/enhanced_mcp_server.py`
- Volume mount paths don't align with GitHub Actions environment

**Root Causes:**
1. **Workspace Path Mismatch**: GitHub Actions uses `/github/workspace` but local configs may use different paths
2. **File Availability Timing**: Repository files may not be available when MCP servers try to start

## Solutions Implemented

### 1. **Pre-Setup Script (`setup_mcp_servers.sh`)**

This script addresses the core issues by:

- **Pre-pulling Docker Images**: Eliminates pull delays during MCP server startup
- **Testing Server Functionality**: Validates each server before including in config
- **Creating Validated Configurations**: Generates configs with only working servers
- **Environment Validation**: Checks Docker, volume mounting, and workspace setup

**Usage:**
```bash
# Run before GitHub Copilot workflow starts MCP servers
./setup_mcp_servers.sh
```

### 2. **Diagnostic Tool (`diagnose_mcp_issues.py`)**

Comprehensive diagnostic tool that:

- **Tests Docker Environment**: Validates Docker availability and functionality
- **Checks Image Accessibility**: Verifies Docker image can be pulled and run
- **Validates Volume Mounting**: Tests workspace file access through Docker
- **Server-Specific Testing**: Tests each MCP server individually
- **Generates Reports**: Provides detailed diagnostics and recommendations

**Usage:**
```bash
python3 diagnose_mcp_issues.py
```

### 3. **Optimized Configurations**

Created multiple configuration files for different scenarios:

1. **`mcp-config-github-actions.json`**: Basic config for GitHub Actions environment
2. **`mcp-config-optimized.json`**: Generated with only tested, working servers
3. **`mcp-config-validated.json`**: Created by setup script with validated servers

### 4. **Enhanced MCP Servers with Better Error Handling**

The `enhanced_mcp_server.py` provides:

- **Improved Logging**: Detailed error messages and execution time tracking
- **Better Timeout Handling**: Configurable timeouts for operations
- **Comprehensive Error Responses**: JSON-RPC compliant error handling
- **Validation**: Input parameter validation and sanitization

## Specific Fixes for GitHub Copilot Workflow Issues

### Issue: Docker Image Pull Timeout

**Solution:**
```bash
# Add this step before "Start MCP Servers" in GitHub Actions workflow
- name: Pre-pull Docker Images
  run: |
    docker pull ghcr.io/millionthodin16/lanbu:latest
    docker images
```

### Issue: Volume Mount Path Problems

**Solution:**
Use consistent workspace paths in MCP configurations:

```json
{
  "args": [ 
    "run", "-i", "--rm", 
    "-v", "/github/workspace:/workspace", 
    "-w", "/workspace", 
    "ghcr.io/millionthodin16/lanbu:latest", 
    "server-command" 
  ]
}
```

### Issue: Server Startup Timeouts

**Solution:**
1. **Use Simple Servers First**: Start with uber-apk-signer and keytool servers
2. **Progressive Loading**: Add complex servers (apktool, ghidra) only after basics work
3. **Implement Timeout Handling**: Use validated configs that exclude problematic servers

### Issue: Enhanced Server File Access

**Solution:**
```json
{
  "args": [ 
    "run", "-i", "--rm", 
    "-v", "/github/workspace:/workspace", 
    "-w", "/workspace", 
    "ghcr.io/millionthodin16/lanbu:latest", 
    "python3", "/workspace/enhanced_mcp_server.py", "server-type"
  ]
}
```

## Recommended Workflow Integration

### Step 1: Add Pre-Setup to GitHub Actions

```yaml
- name: Setup MCP Servers
  run: |
    chmod +x ./setup_mcp_servers.sh
    ./setup_mcp_servers.sh
  working-directory: ${{ github.workspace }}
```

### Step 2: Use Validated Configuration

```yaml
- name: Start MCP Servers
  uses: github/copilot-swe-agent-action@v1
  with:
    mcp-config-path: ./mcp-config-validated.json
```

### Step 3: Fallback Strategy

If MCP servers still fail:

1. **Use Minimal Config**: Start with only 1-2 basic servers
2. **Check Logs**: Use diagnostic script to identify specific issues
3. **Progressive Enhancement**: Add servers one at a time

## Debugging Commands

### Test Docker Environment
```bash
# Test basic Docker functionality
docker run --rm hello-world

# Test our specific image
docker run --rm ghcr.io/millionthodin16/lanbu:latest echo "test"

# Test volume mounting
echo "test" > test.txt
docker run --rm -v $(pwd):/workspace -w /workspace alpine:latest cat test.txt
rm test.txt
```

### Test Individual MCP Servers
```bash
# Test uber-apk-signer server
echo '{"jsonrpc": "2.0", "id": 1, "params": {"args": ["--version"]}}' | \
docker run -i --rm -v $(pwd):/workspace -w /workspace \
ghcr.io/millionthodin16/lanbu:latest uber-apk-signer-mcp-server

# Test keytool server
echo '{"jsonrpc": "2.0", "id": 1, "params": {"args": ["-help"]}}' | \
docker run -i --rm -v $(pwd):/workspace -w /workspace \
ghcr.io/millionthodin16/lanbu:latest keytool-mcp-server
```

### Check GitHub Actions Environment
```bash
# In GitHub Actions workflow
- name: Debug Environment
  run: |
    echo "GITHUB_WORKSPACE: $GITHUB_WORKSPACE"
    echo "PWD: $(pwd)"
    echo "Contents: $(ls -la)"
    echo "Docker version: $(docker --version)"
    echo "Available images: $(docker images)"
```

## Success Criteria

After implementing these fixes, you should see:

1. **"Start MCP Servers" step completes successfully** (no cancellation/timeout)
2. **MCP servers respond to requests** within expected timeframes
3. **GitHub Copilot can utilize MCP tools** for APK analysis tasks
4. **Consistent workflow execution** across multiple runs

## Contact Information

If issues persist after implementing these fixes:

1. **Run the diagnostic script** and include output in issue reports
2. **Provide workflow logs** from the "Start MCP Servers" step
3. **Include MCP configuration** being used
4. **Specify GitHub Actions runner type** and resource constraints

The diagnostic tools will provide specific error details and recommended actions for resolving remaining issues.