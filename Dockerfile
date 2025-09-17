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

# Install apktool
ENV APKTOOL_VERSION=2.9.3
RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}.jar -O /usr/local/bin/apktool.jar && \
    echo '#!/bin/sh\njava -jar /usr/local/bin/apktool.jar "$@"' > /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool

# Install Android SDK Command-line Tools & apksigner
ENV ANDROID_SDK_TOOLS_VERSION=11076708
RUN mkdir -p /opt/android/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_SDK_TOOLS_VERSION}_latest.zip -O /tmp/cmdline-tools.zip && \
    unzip /tmp/cmdline-tools.zip -d /opt/android/cmdline-tools && \
    mv /opt/android/cmdline-tools/cmdline-tools /opt/android/cmdline-tools/latest && \
    rm /tmp/cmdline-tools.zip
ENV PATH=$PATH:/opt/android/cmdline-tools/latest/bin
RUN yes | sdkmanager --licenses && sdkmanager "build-tools;34.0.0"
ENV PATH=$PATH:/opt/android/build-tools/34.0.0

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