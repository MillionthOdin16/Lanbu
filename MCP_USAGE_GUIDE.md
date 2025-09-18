# MCP Server Usage Guide

This repository provides a comprehensive set of MCP (Model Context Protocol) servers for APK analysis and modification. Each server has been thoroughly tested and enhanced with robust error handling, validation, and advanced features.

## Available MCP Servers

### 1. 🔧 Uber APK Signer MCP Server (`uber-apk-signer-mcp-server.py`)

Provides APK signing and verification capabilities using uber-apk-signer.

**Available Tools:**
- `sign_apk` - Sign APK files with custom keystores
- `verify_apk` - Verify APK signatures with detailed output
- `get_apk_info` - Extract APK metadata (size, hash, modification time)
- `check_tool_availability` - Verify uber-apk-signer availability

**Example Usage:**
```bash
# Check if uber-apk-signer is available
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "check_tool_availability", "arguments": {}}}' | python3 uber-apk-signer-mcp-server.py

# Get APK information
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "get_apk_info", "arguments": {"apk_path": "/path/to/app.apk"}}}' | python3 uber-apk-signer-mcp-server.py

# Sign APK with custom keystore
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "sign_apk", "arguments": {"apk_path": "/path/to/app.apk", "keystore_path": "/path/to/keystore.jks", "keystore_pass": "password", "key_alias": "mykey"}}}' | python3 uber-apk-signer-mcp-server.py
```

### 2. 📥 Downloader MCP Server (`downloader.py`)

Provides secure file downloading with integrity verification.

**Available Tools:**
- `download_file` - Download files with size limits and integrity checking
- `get_url_info` - Get detailed URL information with redirect tracking
- `verify_file_integrity` - Verify file integrity using SHA256 hashes

**Example Usage:**
```bash
# Download with integrity verification
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "download_file", "arguments": {"url": "https://example.com/file.apk", "output_path": "/tmp/downloaded.apk", "max_size": 100000000, "expected_hash": "sha256hash"}}}' | python3 downloader.py

# Get URL information with redirect tracking
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "get_url_info", "arguments": {"url": "https://example.com/file", "follow_redirects": true}}}' | python3 downloader.py

# Verify file integrity
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "verify_file_integrity", "arguments": {"file_path": "/path/to/file", "expected_hash": "sha256hash"}}}' | python3 downloader.py
```

### 3. 🔐 Keytool MCP Server (`keytool-mcp-server.py`)

Provides comprehensive keystore and certificate management.

**Available Tools:**
- `generate_keystore` - Generate keystores with custom parameters
- `list_keystore` - List keystore contents with verbose options
- `export_certificate` - Export certificates in DER or PEM format
- `import_certificate` - Import certificates into keystores
- `delete_entry` - Delete keystore entries
- `check_tool_availability` - Verify keytool availability
- `keytool_command` - Execute custom keytool commands

**Example Usage:**
```bash
# Generate keystore for APK signing
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "generate_keystore", "arguments": {"keystore_path": "/tmp/release.keystore", "alias": "releasekey", "dname": "CN=MyApp, O=MyCompany, C=US", "keypass": "keypass123", "storepass": "storepass123", "validity": "365", "keysize": "2048"}}}' | python3 keytool-mcp-server.py

# List keystore contents
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "list_keystore", "arguments": {"keystore_path": "/tmp/release.keystore", "storepass": "storepass123", "verbose": true}}}' | python3 keytool-mcp-server.py

# Export certificate
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "export_certificate", "arguments": {"keystore_path": "/tmp/release.keystore", "alias": "releasekey", "cert_path": "/tmp/cert.der", "storepass": "storepass123", "format": "DER"}}}' | python3 keytool-mcp-server.py
```

### 4. 📱 APKTool MCP Server (External)

Provided by the external `apktool-mcp-server` repository for APK decompilation and recompilation.

### 5. 🔍 Ghidra MCP Server (External)

Provided by the `pyghidra-mcp` package for binary analysis using Ghidra.

## Docker Usage

The repository includes a Docker configuration that provides all tools in a single container:

```bash
# Build the container
docker build -t lanbu .

# Run with volume mapping for your workspace
docker run -i --rm -v /your/workspace:/workspace -w /workspace lanbu python3 uber-apk-signer-mcp-server.py

# Use with MCP configuration
# See mcp-config.sample.json for configuration examples
```

## MCP Configuration

Example MCP client configuration (`mcp-config.sample.json`):

```json
{
  "mcpServers": {
    "apk_signer": {
      "type": "local",
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/workspace:/workspace", "-w", "/workspace", "lanbu", "python3", "uber-apk-signer-mcp-server.py"],
      "tools": ["*"]
    },
    "downloader": {
      "type": "local", 
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/workspace:/workspace", "-w", "/workspace", "lanbu", "python3", "downloader.py"],
      "tools": ["*"]
    },
    "keytool": {
      "type": "local",
      "command": "docker", 
      "args": ["run", "-i", "--rm", "-v", "/workspace:/workspace", "-w", "/workspace", "lanbu", "python3", "keytool-mcp-server.py"],
      "tools": ["*"]
    }
  }
}
```

## Complete APK Analysis Workflow

Here's a complete workflow for analyzing and modifying APK files:

1. **Download APK**:
   ```bash
   # Download with integrity verification
   downloader.download_file(url="https://example.com/app.apk", verify_ssl=true, max_size=100000000)
   ```

2. **Get APK Information**:
   ```bash
   # Extract metadata and verify integrity
   uber_apk_signer.get_apk_info(apk_path="/workspace/app.apk")
   ```

3. **Generate Signing Key**:
   ```bash
   # Create keystore for signing
   keytool.generate_keystore(
       keystore_path="/workspace/release.keystore",
       alias="releasekey", 
       dname="CN=MyApp, O=MyCompany, C=US",
       keypass="keypass123",
       storepass="storepass123"
   )
   ```

4. **Decompile APK** (using APKTool):
   ```bash
   # Decompile for analysis/modification
   apktool.decode_apk(apk_path="/workspace/app.apk", output_dir="/workspace/app_decompiled")
   ```

5. **Analyze with Ghidra** (optional):
   ```bash
   # Deep binary analysis
   ghidra.analyze_apk(apk_path="/workspace/app.apk")
   ```

6. **Recompile and Sign**:
   ```bash
   # Recompile APK
   apktool.build_apk(project_dir="/workspace/app_decompiled", output_apk="/workspace/app_modified.apk")
   
   # Sign the modified APK
   uber_apk_signer.sign_apk(
       apk_path="/workspace/app_modified.apk",
       keystore_path="/workspace/release.keystore",
       keystore_pass="storepass123",
       key_alias="releasekey"
   )
   ```

7. **Verify Final APK**:
   ```bash
   # Verify signature and integrity
   uber_apk_signer.verify_apk(apk_path="/workspace/app_modified_signed.apk", verbose=true)
   ```

## Security Features

All MCP servers include comprehensive security features:

- **Input Validation**: All file paths and parameters are validated
- **File Integrity Verification**: SHA256 hashing for download verification
- **Tool Availability Checking**: Verify tools exist before execution
- **Size Limits**: Prevent resource exhaustion attacks
- **SSL Verification**: Secure HTTPS downloads with certificate validation
- **Path Sanitization**: Prevent directory traversal attacks
- **Error Handling**: Graceful failure with detailed error messages

## Testing

Run the comprehensive test suite to verify all functionality:

```bash
# Basic communication test
python3 test_mcp_basic.py

# Integration test with real APK
python3 test_mcp_integration.py

# Enhanced features test
python3 test_enhanced_features.py
```

## Troubleshooting

### Tool Not Available Errors

If you get "tool not available" errors:

1. **For keytool**: Ensure Java JDK is installed and `keytool` is in PATH
2. **For uber-apk-signer**: Ensure `uber-apk-signer.jar` is in `/usr/local/bin/` or update the path
3. **For APKTool**: Install via the external repository or ensure `apktool` is available
4. **For Ghidra**: Install `pyghidra-mcp` package and ensure Ghidra is properly configured

### Docker Issues

- Ensure Docker is installed and running
- Verify volume mounts are correct for your workspace
- Check that the image was built successfully with all tools

### Network Issues

- Verify internet connectivity for downloads
- Check firewall settings for HTTPS access
- Ensure SSL certificates are valid if `verify_ssl=true`

## Contributing

This MCP server implementation follows best practices:

- **MCP Protocol Compliance**: Full JSON-RPC 2.0 implementation
- **Error Handling**: Comprehensive error codes and messages  
- **Security**: Input validation and secure operations
- **Testing**: Extensive test coverage for all features
- **Documentation**: Clear usage examples and troubleshooting

For issues or enhancements, please ensure:
1. All tests pass
2. Security considerations are addressed
3. Documentation is updated
4. Error handling is comprehensive