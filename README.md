# Lanbu Docker Container

A containerized Android reverse engineering and analysis toolkit containing:

## Included Tools

- **APKTool v2.9.3** - APK decompilation and rebuilding
- **Uber APK Signer v1.3.0** - APK signing and verification  
- **Keytool** - Java keystore management (OpenJDK 21)
- **Ghidra v11.4.2** - NSA's reverse engineering framework
- **Python 3.11** - With pyghidra-mcp integration

## MCP Servers Available

- **apktool-mcp-server** - APKTool integration via Model Context Protocol
- **keytool-mcp-server** - Custom keytool wrapper for MCP

## Building the Container

```bash
docker build -t lanbu:latest .
```

## Usage Examples

### APKTool Operations
```bash
# Decompile an APK
docker run --rm -v $(pwd):/workspace lanbu:latest apktool d /workspace/app.apk

# Rebuild an APK
docker run --rm -v $(pwd):/workspace lanbu:latest apktool b /workspace/app
```

### APK Signing
```bash
# Sign an APK with Uber APK Signer
docker run --rm -v $(pwd):/workspace lanbu:latest \
  java -jar /usr/local/bin/uber-apk-signer.jar --apks /workspace/app.apk
```

### Keystore Management
```bash
# Generate a new keystore
docker run --rm -v $(pwd):/workspace lanbu:latest \
  keytool -genkeypair -alias mykey -keyalg RSA -keysize 2048 \
  -keystore /workspace/my-release-key.keystore
```

### Interactive Shell
```bash
# Get an interactive shell in the container
docker run --rm -it -v $(pwd):/workspace lanbu:latest /bin/bash
```

## Testing

Run the included test script to verify all tools work correctly:

```bash
./test-docker.sh
```

## Recent Fixes

The Dockerfile has been updated to resolve build issues:

- Fixed missing repository (`secfathy/uber-apk-signer-mcp` → removed, not compatible)
- Updated Ghidra to latest stable version (11.1.2 → 11.4.2)
- Corrected Ghidra download URL with proper date
- All tools now build and function correctly

## File Structure

- `/usr/local/bin/` - Executable tools and MCP servers
- `/opt/apktool-mcp-server/` - APKTool MCP server source
- `/opt/ghidra/` - Ghidra installation directory

## Requirements

- Docker Engine
- At least 2GB RAM for container operations
- Storage space for APK files and analysis artifacts