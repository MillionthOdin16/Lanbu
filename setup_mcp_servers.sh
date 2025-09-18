#!/bin/bash
# GitHub Copilot MCP Server Setup Script
# This script addresses the specific issues found in failed workflow runs

set -e

echo "🚀 Setting up MCP servers for GitHub Copilot workflow..."

# Configuration
DOCKER_IMAGE="ghcr.io/millionthodin16/lanbu:latest"
WORKSPACE_DIR="${GITHUB_WORKSPACE:-/github/workspace}"

echo "📍 Workspace directory: $WORKSPACE_DIR"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check command availability
check_command() {
    if command -v "$1" &> /dev/null; then
        log "✅ $1 is available"
        return 0
    else
        log "❌ $1 is not available"
        return 1
    fi
}

# Pre-flight checks
log "🔍 Running pre-flight checks..."

check_command docker || {
    log "❌ Docker is required but not available"
    exit 1
}

check_command curl || {
    log "❌ curl is required but not available"
    exit 1
}

# Check Docker daemon
log "🔍 Checking Docker daemon..."
if docker info &> /dev/null; then
    log "✅ Docker daemon is running"
else
    log "❌ Docker daemon is not running"
    exit 1
fi

# Pre-pull Docker image to avoid timeout during MCP server startup
log "📥 Pre-pulling Docker image: $DOCKER_IMAGE"
if docker pull "$DOCKER_IMAGE"; then
    log "✅ Docker image pulled successfully"
else
    log "❌ Failed to pull Docker image"
    exit 1
fi

# Verify image is available
if docker images -q "$DOCKER_IMAGE" | grep -q .; then
    log "✅ Docker image is available locally"
else
    log "❌ Docker image not found after pull"
    exit 1
fi

# Test basic Docker functionality with our image
log "🧪 Testing Docker container startup..."
if docker run --rm "$DOCKER_IMAGE" echo "Docker test successful"; then
    log "✅ Docker container can start successfully"
else
    log "❌ Docker container failed to start"
    exit 1
fi

# Test volume mounting
log "🧪 Testing volume mounting..."
TEST_FILE="$WORKSPACE_DIR/docker_mount_test"
echo "test content" > "$TEST_FILE"

if docker run --rm -v "$WORKSPACE_DIR:/workspace" -w /workspace "$DOCKER_IMAGE" cat docker_mount_test 2>/dev/null | grep -q "test content"; then
    log "✅ Volume mounting works correctly"
    rm -f "$TEST_FILE"
else
    log "❌ Volume mounting failed"
    rm -f "$TEST_FILE"
    exit 1
fi

# Test individual MCP servers with short timeout
log "🧪 Testing MCP servers..."

test_mcp_server() {
    local server_name="$1"
    local server_command="$2"
    
    log "Testing $server_name..."
    
    # Create a test request
    local test_request='{"jsonrpc": "2.0", "id": 1, "params": {"args": ["--version"]}}'
    
    # Start server with timeout
    local output
    if output=$(timeout 10s bash -c "echo '$test_request' | docker run -i --rm -v '$WORKSPACE_DIR:/workspace' -w /workspace '$DOCKER_IMAGE' '$server_command' 2>&1"); then
        if echo "$output" | grep -q '"jsonrpc"'; then
            log "✅ $server_name responded correctly"
            return 0
        else
            log "⚠️  $server_name started but no JSON-RPC response"
            return 1
        fi
    else
        log "❌ $server_name failed to start or timed out"
        return 1
    fi
}

# Test core MCP servers
declare -A SERVER_STATUS

test_mcp_server "uber-apk-signer-mcp-server" "uber-apk-signer-mcp-server"
SERVER_STATUS["apk_signer"]=$?

test_mcp_server "keytool-mcp-server" "keytool-mcp-server"
SERVER_STATUS["keytool"]=$?

test_mcp_server "downloader-mcp-server" "downloader-mcp-server"
SERVER_STATUS["downloader"]=$?

# Test apktool server (more complex, just check if it starts)
log "Testing apktool-mcp-server..."
if timeout 15s docker run --rm -v "$WORKSPACE_DIR:/workspace" -w /workspace "$DOCKER_IMAGE" apktool-mcp-server --help &>/dev/null; then
    log "✅ apktool-mcp-server is available"
    SERVER_STATUS["apktool"]=0
else
    log "⚠️  apktool-mcp-server may have issues"
    SERVER_STATUS["apktool"]=1
fi

# Create optimized MCP configuration based on test results
log "📝 Creating optimized MCP configuration..."

# Start with basic structure
cat > "$WORKSPACE_DIR/mcp-config-validated.json" << 'EOF'
{
  "mcpServers": {
EOF

# Build JSON content dynamically
WORKING_SERVERS=0
JSON_CONTENT=""

if [ "${SERVER_STATUS[apk_signer]}" -eq 0 ]; then
    if [ "$WORKING_SERVERS" -gt 0 ]; then
        JSON_CONTENT="$JSON_CONTENT,"
    fi
    JSON_CONTENT="$JSON_CONTENT
    \"apk_signer\": {
      \"type\": \"local\",
      \"command\": \"docker\",
      \"args\": [ 
        \"run\", \"-i\", \"--rm\", 
        \"-v\", \"/github/workspace:/workspace\", 
        \"-w\", \"/workspace\", 
        \"ghcr.io/millionthodin16/lanbu:latest\", 
        \"uber-apk-signer-mcp-server\" 
      ],
      \"tools\": [\"*\"]
    }"
    ((WORKING_SERVERS++))
fi

if [ "${SERVER_STATUS[keytool]}" -eq 0 ]; then
    if [ "$WORKING_SERVERS" -gt 0 ]; then
        JSON_CONTENT="$JSON_CONTENT,"
    fi
    JSON_CONTENT="$JSON_CONTENT
    \"keytool_generator\": {
      \"type\": \"local\",
      \"command\": \"docker\",
      \"args\": [ 
        \"run\", \"-i\", \"--rm\", 
        \"-v\", \"/github/workspace:/workspace\", 
        \"-w\", \"/workspace\", 
        \"ghcr.io/millionthodin16/lanbu:latest\", 
        \"keytool-mcp-server\" 
      ],
      \"tools\": [\"*\"]
    }"
    ((WORKING_SERVERS++))
fi

if [ "${SERVER_STATUS[downloader]}" -eq 0 ]; then
    if [ "$WORKING_SERVERS" -gt 0 ]; then
        JSON_CONTENT="$JSON_CONTENT,"
    fi
    JSON_CONTENT="$JSON_CONTENT
    \"downloader\": {
      \"type\": \"local\",
      \"command\": \"docker\",
      \"args\": [ 
        \"run\", \"-i\", \"--rm\", 
        \"-v\", \"/github/workspace:/workspace\", 
        \"-w\", \"/workspace\", 
        \"ghcr.io/millionthodin16/lanbu:latest\", 
        \"downloader-mcp-server\" 
      ],
      \"tools\": [\"*\"]
    }"
    ((WORKING_SERVERS++))
fi

if [ "${SERVER_STATUS[apktool]}" -eq 0 ]; then
    if [ "$WORKING_SERVERS" -gt 0 ]; then
        JSON_CONTENT="$JSON_CONTENT,"
    fi
    JSON_CONTENT="$JSON_CONTENT
    \"apk_tool\": {
      \"type\": \"local\",
      \"command\": \"docker\",
      \"args\": [ 
        \"run\", \"-i\", \"--rm\", 
        \"-v\", \"/github/workspace:/workspace\", 
        \"-w\", \"/workspace\", 
        \"ghcr.io/millionthodin16/lanbu:latest\", 
        \"apktool-mcp-server\" 
      ],
      \"tools\": [\"*\"],
      \"env\": {
        \"APKTOOL_WORKSPACE\": \"/workspace/apktool_workspace\"
      }
    }"
    ((WORKING_SERVERS++))
fi

# Write complete JSON file
cat > "$WORKSPACE_DIR/mcp-config-validated.json" << EOF
{
  "mcpServers": {$JSON_CONTENT
  }
}
EOF

# Add Ghidra server if we have working servers (it's more complex)
if [ "$WORKING_SERVERS" -gt 0 ]; then
    log "📝 Adding Ghidra analyzer to configuration..."
    
    # Create enhanced config with Ghidra
    cp "$WORKSPACE_DIR/mcp-config-validated.json" "$WORKSPACE_DIR/mcp-config-validated-full.json"
    
    # Insert Ghidra config before the last server
    sed -i '/^  }$/i\
    "ghidra_analyzer": {\
      "type": "local",\
      "command": "docker",\
      "args": [ \
        "run", "-i", "--rm", \
        "-v", "/github/workspace:/workspace", \
        "-w", "/workspace", \
        "ghcr.io/millionthodin16/lanbu:latest", \
        "pyghidra-mcp", "-t", "stdio" \
      ],\
      "tools": ["*"],\
      "env": {\
        "GHIDRA_INSTALL_DIR": "/opt/ghidra",\
        "JAVA_HOME": "/usr/lib/jvm/java-21-openjdk-amd64"\
      }\
    },' "$WORKSPACE_DIR/mcp-config-validated-full.json"
fi

# Report results
log "📊 SETUP SUMMARY"
log "=================="
log "Working MCP servers: $WORKING_SERVERS"

for server in apk_signer keytool downloader apktool; do
    if [ "${SERVER_STATUS[$server]}" -eq 0 ]; then
        log "✅ $server: Working"
    else
        log "❌ $server: Issues detected"
    fi
done

log "📁 Configuration files created:"
log "  - mcp-config-validated.json (tested servers only)"
if [ -f "$WORKSPACE_DIR/mcp-config-validated-full.json" ]; then
    log "  - mcp-config-validated-full.json (includes Ghidra)"
fi

# Provide recommendations
if [ "$WORKING_SERVERS" -eq 0 ]; then
    log "❌ CRITICAL: No working MCP servers found"
    log "💡 RECOMMENDATION: Check Docker image and container environment"
    exit 1
elif [ "$WORKING_SERVERS" -lt 3 ]; then
    log "⚠️  WARNING: Limited MCP servers working ($WORKING_SERVERS/4)"
    log "💡 RECOMMENDATION: Use mcp-config-validated.json for reliable operation"
else
    log "🎉 SUCCESS: Most MCP servers are working"
    log "💡 RECOMMENDATION: Use mcp-config-validated-full.json for full functionality"
fi

# Set up environment for GitHub Actions
if [ -n "$GITHUB_ENV" ]; then
    echo "MCP_CONFIG_FILE=$WORKSPACE_DIR/mcp-config-validated.json" >> "$GITHUB_ENV"
    echo "MCP_SERVERS_WORKING=$WORKING_SERVERS" >> "$GITHUB_ENV"
    log "📝 Environment variables set for GitHub Actions"
fi

log "✅ MCP server setup completed successfully"