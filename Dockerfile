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

# --- Install Apktool MCP Server ---
RUN git clone https://github.com/zinja-coder/apktool-mcp-server.git /opt/apktool-mcp-server && \
    sed -i '/logging/d' /opt/apktool-mcp-server/requirements.txt && \
    pip install -r /opt/apktool-mcp-server/requirements.txt && \
    echo '#!/bin/sh\npython3 /opt/apktool-mcp-server/main.py "$@"' > /usr/local/bin/apktool-mcp-server && \
    chmod +x /usr/local/bin/apktool-mcp-server

# --- Install Uber APK Signer ---
ENV UBER_APK_SIGNER_VERSION=1.3.0
RUN wget https://github.com/patrickfav/uber-apk-signer/releases/download/v${UBER_APK_SIGNER_VERSION}/uber-apk-signer-${UBER_APK_SIGNER_VERSION}.jar -O /usr/local/bin/uber-apk-signer.jar

# Note: uber-apk-signer-mcp is not available in a compatible Python version
# The uber-apk-signer.jar can be used directly via Java commands

# --- Add the custom Keytool MCP Server wrapper ---
COPY keytool-mcp-server.py /usr/local/bin/keytool-mcp-server
RUN chmod +x /usr/local/bin/keytool-mcp-server

# Install Ghidra
ENV GHIDRA_VERSION=11.4.2
ENV GHIDRA_INSTALL_DIR=/opt/ghidra
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
RUN wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_PUBLIC_20250826.zip -O /tmp/ghidra.zip && \
    unzip /tmp/ghidra.zip -d /opt && \
    mv /opt/ghidra_${GHIDRA_VERSION}_PUBLIC ${GHIDRA_INSTALL_DIR} && \
    rm /tmp/ghidra.zip

# Install pyghidra-mcp
RUN pip install pyghidra-mcp
