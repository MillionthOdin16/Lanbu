# GitHub Copilot MCP Server Troubleshooting Guide

This guide addresses the specific issues found in GitHub Copilot workflow runs where MCP servers fail to start or time out.

## Issues Identified from Workflow Logs

### 1. **MCP Protocol Compliance Issues**

**Symptoms:**
- MCP servers fail with validation errors like:
  ```
  "code": "invalid_type",
  "expected": "string", 
  "received": "undefined",
  "path": ["protocolVersion"],
  "message": "Required"
  ```
- Missing `capabilities` and `serverInfo` in initialization response

**Root Cause:**
The original custom MCP servers (`uber-apk-signer-mcp-server.py`, `keytool-mcp-server.py`, `downloader.py`) were implemented as simple JSON-RPC servers but were **not implementing the full MCP (Model Context Protocol) specification**.

GitHub Copilot's MCP client expects:
1. **Proper initialization handshake** with `initialize` method
2. **Protocol version negotiation** (`protocolVersion: "2024-11-05"`)
3. **Capability declaration** (`capabilities` object)
4. **Server information** (`serverInfo` with name and version)
5. **Tools listing** via `tools/list` method
6. **Tool execution** via `tools/call` method

**Solution Applied:**
Updated all custom MCP servers to implement the full MCP protocol specification, including proper initialization, capabilities, and tool management.

### 2. **"Start MCP Servers" Step Cancellation/Timeout**

**Symptoms:**
- Workflow step "Start MCP Servers" shows as "cancelled" 
- Log shows "MCP Tool server started successfully" followed by "##[error]The operation was canceled."
- Timeout after ~53 seconds during server startup

**Root Causes:**
1. **Docker Image Pull Delays**: GitHub Copilot workflows don't pre-pull the Docker image, causing timeouts during first-time pulls
2. **Volume Mount Issues**: Incorrect workspace path mapping between GitHub Actions environment and Docker containers
3. **Server Startup Timeouts**: Complex MCP servers like apktool-mcp-server take longer to initialize than the workflow timeout allows
4. **Resource Constraints**: GitHub Actions runners may have limited resources affecting Docker container startup

### 3. **Configuration Path Issues**

**Symptoms:**
- Enhanced servers fail to start when referencing `/workspace/enhanced_mcp_server.py`
- Volume mount paths don't align with GitHub Actions environment

**Root Causes:**
1. **Workspace Path Mismatch**: GitHub Actions uses `/github/workspace` but local configs may use different paths
2. **File Availability Timing**: Repository files may not be available when MCP servers try to start

## Solutions Implemented

### 1. **MCP Protocol Compliance Fix**

**Updated Server Implementation:**
All custom MCP servers now properly implement the MCP protocol:

```python
# MCP Protocol Implementation
MCP_VERSION = "2024-11-05"

def handle_initialize(id, params):
    """Handle MCP initialize request."""
    send_response(id, {
        "protocolVersion": MCP_VERSION,
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "server-name",
            "version": "1.0.0"
        }
    })

def handle_tools_list(id, params):
    """Handle tools/list request."""
    send_response(id, {
        "tools": [
            {
                "name": "tool_name",
                "description": "Tool description",
                "inputSchema": {...}
            }
        ]
    })

def handle_tools_call(id, params):
    """Handle tools/call request."""
    # Execute tool and return results in MCP format
    send_response(id, {
        "content": [
            {
                "type": "text",
                "text": "Tool output"
            }
        ],
        "isError": False
    })
```

### 2. **Pre-Setup Script (`setup_mcp_simple.py`)**

This script addresses the core issues by:

- **Pre-pulling Docker Images**: Eliminates pull delays during MCP server startup
- **Testing Server Functionality**: Validates each server before including in config
- **Creating Validated Configurations**: Generates configs with only working servers
- **Environment Validation**: Checks Docker, volume mounting, and workspace setup

**Usage:**
```bash
# Run before GitHub Copilot workflow starts MCP servers
python3 setup_mcp_simple.py
```

### 3. **Diagnostic Tool (`diagnose_mcp_issues.py`)**

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

### 4. **Optimized Configurations**

Created multiple configuration files for different scenarios:

1. **`mcp-config-github-copilot.json`**: Optimized for GitHub Copilot workflows
2. **`mcp-config-validated.json`**: Generated with only tested, working servers
3. **`mcp-config.sample.json`**: Updated sample configuration

## Specific Fixes for GitHub Copilot Workflow Issues

### Issue: MCP Protocol Validation Errors

**Solution:**
Updated all MCP servers to implement proper MCP protocol:
```yaml
# Configuration now uses proper MCP-compliant servers
"apk_signer": {
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
```

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
    "python3", "server-script.py" 
  ]
}
```

### Issue: Server Startup Timeouts

**Solution:**
1. **Use MCP-Compliant Servers**: Proper MCP initialization is faster and more reliable
2. **Progressive Loading**: Start with basic servers (apk_signer, keytool, downloader)
3. **Pre-Setup Validation**: Use validated configs that exclude problematic servers

## Recommended Workflow Integration

### Step 1: Add Pre-Setup to GitHub Actions

```yaml
- name: Setup MCP Servers
  run: |
    python3 setup_mcp_simple.py
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

### Test MCP Protocol Compliance
```bash
# Test MCP initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | \
docker run -i --rm -v $(pwd):/workspace -w /workspace \
ghcr.io/millionthodin16/lanbu:latest python3 uber-apk-signer-mcp-server.py

# Test tools listing
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}'; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}') | \
docker run -i --rm -v $(pwd):/workspace -w /workspace \
ghcr.io/millionthodin16/lanbu:latest python3 uber-apk-signer-mcp-server.py
```

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

## Latest Resolution Summary

**2025-09-18: MCP Protocol Compliance Issue Resolved**

The core issue was that custom MCP servers were not implementing the MCP protocol specification. GitHub Copilot's MCP client expected proper initialization handshakes with `protocolVersion`, `capabilities`, and `serverInfo`, but the servers were only implementing basic JSON-RPC.

**Servers Fixed:**
- `uber-apk-signer-mcp-server.py`: Now MCP-compliant
- `keytool-mcp-server.py`: Now MCP-compliant  
- `downloader.py`: Now MCP-compliant

**Validation Results:**
- ✅ All 3 custom MCP servers pass MCP protocol tests
- ✅ Docker environment working correctly
- ✅ APK file accessible (34MB confirmed)
- ✅ Setup script creates validated configurations

**Quick Fix for GitHub Copilot:**
Use `mcp-config-validated.json` which contains only tested, MCP-compliant servers.

## Contact Information

If issues persist after implementing these fixes:

1. **Run the diagnostic script** and include output in issue reports
2. **Provide workflow logs** from the "Start MCP Servers" step
3. **Include MCP configuration** being used
4. **Specify GitHub Actions runner type** and resource constraints

The diagnostic tools will provide specific error details and recommended actions for resolving remaining issues.