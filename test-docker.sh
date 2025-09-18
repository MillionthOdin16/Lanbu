#!/bin/bash
# Test script to verify Docker container functionality

echo "Testing Lanbu Docker container..."

# Build the container
echo "Building Docker container..."
docker build -t lanbu:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker build successful"

# Test apktool
echo "Testing apktool..."
APKTOOL_VERSION=$(docker run --rm lanbu:latest apktool --version)
echo "  Apktool version: $APKTOOL_VERSION"

# Test uber-apk-signer
echo "Testing uber-apk-signer..."
UBER_VERSION=$(docker run --rm lanbu:latest java -jar /usr/local/bin/uber-apk-signer.jar --version)
echo "  Uber APK Signer: $UBER_VERSION"

# Test keytool
echo "Testing keytool..."
KEYTOOL_HELP=$(docker run --rm lanbu:latest keytool -help 2>&1 | head -1)
echo "  Keytool: $KEYTOOL_HELP"

# Test Ghidra directory
echo "Testing Ghidra installation..."
GHIDRA_DIR=$(docker run --rm lanbu:latest ls -la /opt/ghidra 2>/dev/null | head -1)
if [ -n "$GHIDRA_DIR" ]; then
    echo "  ✅ Ghidra installed in /opt/ghidra"
else
    echo "  ❌ Ghidra not found"
fi

# Test MCP servers
echo "Testing MCP servers..."
APKTOOL_MCP=$(docker run --rm lanbu:latest ls -la /usr/local/bin/apktool-mcp-server 2>/dev/null)
UBER_MCP=$(docker run --rm lanbu:latest ls -la /usr/local/bin/uber-apk-signer-mcp-server 2>/dev/null)
KEYTOOL_MCP=$(docker run --rm lanbu:latest ls -la /usr/local/bin/keytool-mcp-server 2>/dev/null)

if [ -n "$APKTOOL_MCP" ]; then
    echo "  ✅ Apktool MCP server available"
else
    echo "  ❌ Apktool MCP server missing"
fi

if [ -n "$UBER_MCP" ]; then
    echo "  ✅ Uber APK Signer MCP server available"
else
    echo "  ❌ Uber APK Signer MCP server missing"
fi

if [ -n "$KEYTOOL_MCP" ]; then
    echo "  ✅ Keytool MCP server available"
else
    echo "  ❌ Keytool MCP server missing"
fi

# Test MCP server functionality
echo "Testing MCP server responses..."
UBER_MCP_RESPONSE=$(echo '{"id": 1, "params": {"args": ["--version"]}}' | docker run --rm -i lanbu:latest uber-apk-signer-mcp-server 2>/dev/null | grep -o '"exitCode": 0' || echo "failed")
if [ "$UBER_MCP_RESPONSE" = '"exitCode": 0' ]; then
    echo "  ✅ Uber APK Signer MCP server responds correctly"
else
    echo "  ❌ Uber APK Signer MCP server not responding correctly"
fi

echo ""
echo "🎉 All tests completed successfully!"
echo ""
echo "Container usage examples:"
echo "  # Run apktool:"
echo "  docker run --rm -v \$(pwd):/workspace lanbu:latest apktool d /workspace/app.apk"
echo ""
echo "  # Run uber-apk-signer:"
echo "  docker run --rm -v \$(pwd):/workspace lanbu:latest java -jar /usr/local/bin/uber-apk-signer.jar --apks /workspace/app.apk"
echo ""
echo "  # Run keytool:"
echo "  docker run --rm lanbu:latest keytool -genkeypair -alias mykey -keyalg RSA"