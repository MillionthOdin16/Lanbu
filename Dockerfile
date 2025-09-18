# Start from a base image with Python
FROM python:3.11-slim

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install all dependencies at build time
RUN apt-get update && apt-get install -y \
    openjdk-21-jdk-headless \
    wget \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install original apktool (can be used by the MCP server)
ENV APKTOOL_VERSION=2.9.3
RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}.jar -O /usr/local/bin/apktool.jar && \
    echo '#!/bin/sh\njava -jar /usr/local/bin/apktool.jar "$@"' > /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool

# --- NEW: Install Apktool MCP Server ---
RUN git clone https://github.com/zinja-coder/apktool-mcp-server.git /opt/apktool-mcp-server && \
    pip install -r /opt/apktool-mcp-server/requirements.txt && \
    echo '#!/bin/sh\npython3 /opt/apktool-mcp-server/main.py "$@"' > /usr/local/bin/apktool-mcp-server && \
    chmod +x /usr/local/bin/apktool-mcp-server

# --- NEW: Install Uber APK Signer and its MCP Server ---
# Install uber-apk-signer jar
ENV UBER_APK_SIGNER_VERSION=1.3.0
RUN wget https://github.com/patrickfav/uber-apk-signer/releases/download/v${UBER_APK_SIGNER_VERSION}/uber-apk-signer-v${UBER_APK_SIGNER_VERSION}.jar -O /usr/local/bin/uber-apk-signer.jar

# Install the MCP server for uber-apk-signer
RUN git clone https://github.com/secfathy/uber-apk-signer-mcp.git /opt/uber-apk-signer-mcp && \
    pip install -r /opt/uber-apk-signer-mcp/requirements.txt && \
    echo '#!/bin/sh\npython3 /opt/uber-apk-signer-mcp/main.py --uber-apk-signer-path /usr/local/bin/uber-apk-signer.jar "$@"' > /usr/local/bin/uber-apk-signer-mcp && \
    chmod +x /usr/local/bin/uber-apk-signer-mcp

# --- NEW: Create a custom Keytool MCP Server wrapper ---
RUN echo '#!/usr/bin/env python3
import sys
import json
import subprocess

def send_response(id, result):
    response = {"jsonrpc": "2.0", "id": id, "result": result}
    print(json.dumps(response), flush=True)

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        request = json.loads(line)
        id = request.get("id")
        params = request.get("params", {})
        command = params.get("args", [])

        try:
            # Execute keytool with the provided arguments
            process = subprocess.run(
                ["keytool"] + command,
                capture_output=True,
                text=True,
                check=False
            )
            output = f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
            send_response(id, {"output": output, "exitCode": process.returncode})
        except Exception as e:
            send_response(id, {"output": str(e), "exitCode": 1})

if __name__ == "__main__":
    main()
' > /usr/local/bin/keytool-mcp-server && \
    chmod +x /usr/local/bin/keytool-mcp-server

# Install Ghidra (no changes here)
ENV GHIDRA_VERSION=11.1.2
ENV GHIDRA_INSTALL_DIR=/opt/ghidra
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
RUN wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_PUBLIC_20240723.zip -O /tmp/ghidra.zip && \
    unzip /tmp/ghidra.zip -d /opt && \
    mv /opt/ghidra_${GHIDRA_VERSION}_PUBLIC ${GHIDRA_INSTALL_DIR} && \
    rm /tmp/ghidra.zip

# Install pyghidra-mcp (no changes here)
RUN pip install pyghidra-mcp
