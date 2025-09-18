# MCP Server and APK Analysis Setup

This repository provides a comprehensive Docker-based environment for APK analysis with multiple MCP (Model Context Protocol) servers.

## Available MCP Servers

### 1. APKTool MCP Server
- **Command:** `apktool-mcp-server`
- **Description:** Advanced APK decompilation and recompilation using APKTool
- **Features:** FastMCP-based server with comprehensive APK manipulation tools
- **Status:** ✅ Working (requires proper MCP initialization sequence)

### 2. Uber APK Signer MCP Server
- **Command:** `uber-apk-signer-mcp-server`
- **Description:** APK signing and verification using Uber APK Signer
- **Features:** JSON-RPC interface for APK signing operations
- **Status:** ✅ Working

### 3. Keytool MCP Server
- **Command:** `keytool-mcp-server`
- **Description:** Java keystore management operations
- **Features:** Generate certificates, manage keystores
- **Status:** ✅ Working

### 4. Downloader MCP Server
- **Command:** `downloader-mcp-server`
- **Description:** Download files from URLs to workspace
- **Features:** Simple file download with JSON-RPC interface
- **Status:** ✅ Working

### 5. Ghidra Analyzer MCP Server
- **Command:** `pyghidra-mcp`
- **Description:** Binary analysis using Ghidra
- **Features:** Reverse engineering and code analysis
- **Status:** ✅ Available (through pyghidra-mcp package)

## Sample Configuration

The `mcp-config.sample.json` file provides a complete configuration for using these servers with GitHub Copilot or other MCP clients:

```json
{
  "mcpServers": {
    "ghidra_analyzer": {
      "type": "local",
      "command": "docker",
      "args": [ "run", "-i", "--rm", "-v", "/github/workspace:/workspace", "-w", "/workspace", "ghcr.io/millionthodin16/lanbu:latest", "pyghidra-mcp", "-t", "stdio" ],
      "tools": ["*"]
    },
    "apk_tool": {
      "type": "local",
      "command": "docker",
      "args": [ "run", "-i", "--rm", "-v", "/github/workspace:/workspace", "-w", "/workspace", "ghcr.io/millionthodin16/lanbu:latest", "apktool-mcp-server" ],
      "tools": ["*"]
    },
    "apk_signer": {
      "type": "local",
      "command": "docker",
      "args": [ "run", "-i", "--rm", "-v", "/github/workspace:/workspace", "-w", "/workspace", "ghcr.io/millionthodin16/lanbu:latest", "uber-apk-signer-mcp-server" ],
      "tools": ["*"]
    },
    "keytool_generator": {
      "type": "local",
      "command": "docker",
      "args": [ "run", "-i", "--rm", "-v", "/github/workspace:/workspace", "-w", "/workspace", "ghcr.io/millionthodin16/lanbu:latest", "keytool-mcp-server" ],
      "tools": ["*"]
    },
    "downloader": {
      "type": "local",
      "command": "docker",
      "args": [ "run", "-i", "--rm", "-v", "/github/workspace:/workspace", "-w", "/workspace", "ghcr.io/millionthodin16/lanbu:latest", "downloader-mcp-server" ],
      "tools": ["*"]
    }
  }
}
```

## APK File Location

The repository includes a sample APK file:
- **File:** `com.Glowbeast.LanBu v0.53.apk`
- **Size:** ~34MB
- **Location:** Repository root directory
- **Accessibility:** ✅ Verified accessible within Docker containers

## Usage Examples

### Testing MCP Servers

Use the provided test script to verify all servers are working:

```bash
python3 test_mcp_servers.py
```

### Using Individual Servers

#### Uber APK Signer
```bash
echo '{"jsonrpc": "2.0", "id": 1, "params": {"args": ["--version"]}}' | \
docker run -i --rm -v $(pwd):/workspace -w /workspace ghcr.io/millionthodin16/lanbu:latest uber-apk-signer-mcp-server
```

#### Keytool
```bash
echo '{"jsonrpc": "2.0", "id": 1, "params": {"args": ["-help"]}}' | \
docker run -i --rm -v $(pwd):/workspace -w /workspace ghcr.io/millionthodin16/lanbu:latest keytool-mcp-server
```

#### Downloader
```bash
echo '{"jsonrpc": "2.0", "id": 1, "params": {"url": "https://example.com/file.apk"}}' | \
docker run -i --rm -v $(pwd):/workspace -w /workspace ghcr.io/millionthodin16/lanbu:latest downloader-mcp-server
```

#### APKTool (requires proper MCP initialization)
```bash
# Initialize first
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | \
docker run -i --rm -v $(pwd):/workspace -w /workspace ghcr.io/millionthodin16/lanbu:latest apktool-mcp-server
```

## Historical Issues (Resolved)

The following issues were encountered and resolved during development:

1. **Build Failures with External Dependencies**
   - **Issue:** Failed attempts to clone private/non-existent repositories
   - **Resolution:** Implemented local Python scripts instead of external dependencies

2. **MCP Protocol Compliance**
   - **Issue:** Some servers required proper MCP initialization sequences
   - **Resolution:** Implemented FastMCP framework for apktool-mcp-server

3. **Docker Container Tool Availability**
   - **Issue:** Missing required tools in container
   - **Resolution:** Comprehensive installation of Java, APKTool, Python, and related tools

## Architecture

```
Docker Container (ghcr.io/millionthodin16/lanbu:latest)
├── Base: Python 3.11-slim
├── Java 21 OpenJDK
├── APKTool 2.9.3
├── Uber APK Signer 1.3.0
├── Ghidra 11.4.2
├── Python MCP Servers (Custom)
│   ├── uber-apk-signer-mcp-server.py
│   ├── keytool-mcp-server.py
│   └── downloader.py
└── External MCP Servers
    ├── apktool-mcp-server (FastMCP)
    └── pyghidra-mcp
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Responding**
   - Ensure proper initialization sequence for APKTool MCP server
   - Check Docker container has access to workspace volume

2. **APK File Not Found**
   - Verify APK file exists in repository root
   - Check volume mount permissions

3. **Tool Not Available**
   - Run the test script to verify all tools are installed
   - Check Docker image version

### Debug Commands

```bash
# Test container tools
docker run --rm ghcr.io/millionthodin16/lanbu:latest java -version
docker run --rm ghcr.io/millionthodin16/lanbu:latest apktool --version
docker run --rm ghcr.io/millionthodin16/lanbu:latest python3 --version

# Test APK file access
docker run --rm -v $(pwd):/workspace -w /workspace ghcr.io/millionthodin16/lanbu:latest ls -la "*.apk"
```

## Contributing

When adding new MCP servers:

1. Follow the JSON-RPC protocol specification
2. Add comprehensive error handling
3. Include the server in the test suite
4. Update this documentation
5. Ensure Docker container compatibility

## License

This project follows the repository's license terms.