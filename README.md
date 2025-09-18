# LanBu APK Development Project

This repository contains the setup and tools for analyzing and modifying the LanBu Android game APK.

## Project Overview

**LanBu** is a Unity-based Android game (version 0.53) developed by Glowbeast. This project provides a complete development environment for:

- APK decompilation and analysis
- Binary reverse engineering with Ghidra
- Resource modification and recompilation
- APK re-signing and packaging

## Quick Start

### 1. Set Up Development Environment

```bash
# Run the automated setup script
./setup_development.sh
```

This creates a complete workspace in `lanbu_workspace/` with:
- Extracted APK contents
- Analysis tools and scripts
- Organized directory structure for modifications

### 2. Analyze the App

```bash
cd lanbu_workspace/tools/

# Analyze Unity components
./analyze_unity.sh

# Analyze Firebase configuration
./analyze_firebase.sh

# Analyze native libraries (requires additional tools)
./analyze_native.sh

# Analyze Java/Kotlin code (requires jadx or dex2jar)
./analyze_dex.sh
```

### 3. Make Modifications

1. Copy files from `lanbu_workspace/extracted/` to `lanbu_workspace/modified/`
2. Edit the files in the `modified/` directory
3. Use the rebuild script to create a new APK

## App Architecture

### Technology Stack
- **Unity Engine**: Game framework with IL2CPP backend
- **Firebase**: Analytics and services
- **VoxelBusters Essential Kit**: Cross-platform native functionality
- **Google Mobile Ads**: Advertisement integration
- **AndroidX Libraries**: Modern Android components

### Key Components

#### Native Libraries (70+ MB total)
- `libil2cpp.so` (49.5 MB) - Unity IL2CPP runtime containing C# game logic
- `libunity.so` (14.5 MB) - Core Unity engine
- `libFirebaseCppApp-12_8_0.so` (4.3 MB) - Firebase integration
- `libgame.so` (142 KB) - Game-specific native code

#### Compiled Code (16+ MB total)
- `classes.dex` (8.6 MB) - Primary Java/Kotlin code
- `classes2.dex` (8.1 MB) - Additional Java/Kotlin code
- `classes3.dex` (3.6 KB) - Minimal additional code

#### Unity Assets
- `data.unity3d` (2 MB) - Main game asset bundle
- Global metadata and managed assemblies
- Runtime initialization configuration

## Development Tools Available

### Containerized Environment
The project includes a Dockerfile with pre-configured tools:
- **APKTool 2.9.3**: For APK decompilation/recompilation
- **Ghidra 11.4.2**: For binary analysis and reverse engineering
- **Uber APK Signer**: For re-signing modified APKs
- **Java 21 & Python 3.11**: Development runtimes

### MCP Servers
Model Context Protocol servers for tool integration:
- `apk_tool`: APKTool operations
- `ghidra_analyzer`: Binary analysis
- `apk_signer`: APK signing
- `keytool_generator`: Key management

## Firebase Configuration

The app connects to Firebase project `lanbu-43608`:
- **Project ID**: `lanbu-43608`
- **Package Name**: `com.Glowbeast.LanBu`
- **Services**: Analytics, Cloud Storage
- **API Key**: `AIzaSyAnAqhR2abrLhmyMYDLYpQUgXQeR1EoqIQ`

## Modification Strategies

### 1. Resource Modifications (Easiest)
- **Location**: `res/` directory
- **Target**: UI elements, images, strings
- **Tools**: Image editors, text editors
- **Difficulty**: ⭐ Easy

### 2. Java/Kotlin Logic (Medium)
- **Location**: `classes.dex` files
- **Target**: Android app logic, UI behavior
- **Tools**: jadx, dex2jar, smali/baksmali
- **Difficulty**: ⭐⭐ Medium

### 3. Unity Game Logic (Hard)
- **Location**: `libil2cpp.so`, Unity assets
- **Target**: Core game mechanics
- **Tools**: IL2CPP dumpers, Unity asset extractors
- **Difficulty**: ⭐⭐⭐ Hard

### 4. Native Code (Expert)
- **Location**: `libgame.so`, `libunity.so`
- **Target**: Low-level game functions
- **Tools**: Ghidra, IDA Pro, Hex editors
- **Difficulty**: ⭐⭐⭐⭐ Expert

## File Structure

```
lanbu_workspace/
├── original/           # Original APK files
├── extracted/          # Extracted APK contents (ZIP extraction)
├── decompiled/         # Decompiled source code
├── modified/           # Modified files for rebuilding
├── tools/              # Analysis and build scripts
├── README.md           # Workspace documentation
└── ANALYSIS_SUMMARY.md # Current analysis status
```

## Known Issues and Limitations

1. **MCP Server Path Issues**: APKTool and Ghidra MCP servers have path resolution issues
2. **IL2CPP Complexity**: C# game logic is compiled to native code, making analysis challenging
3. **Certificate Pinning**: App may use Firebase certificate pinning
4. **Anti-Tampering**: Unknown if the app has integrity checks

## Next Steps

1. **Resolve MCP Server Issues**: Fix path mapping for automated tooling
2. **Install Analysis Tools**: Set up jadx, IL2CPP dumpers, Unity asset extractors
3. **Deep Binary Analysis**: Use Ghidra to analyze native libraries
4. **Create Modification Workflow**: Establish reliable APK rebuild and re-sign process
5. **Document Game Mechanics**: Understand core game functionality for targeted modifications

## Security and Legal Notes

- This project is for educational and research purposes
- Respect the original developer's intellectual property
- Be aware of potential DMCA or licensing implications
- Firebase integration may have terms of service restrictions

## Contributing

When making modifications:
1. Document changes thoroughly
2. Test modifications on different devices
3. Verify Firebase functionality if modified
4. Ensure APK signatures are valid
5. Share findings and tools with the community

## Resources

- [APKTool Documentation](https://ibotpeaches.github.io/Apktool/)
- [Ghidra User Guide](https://ghidra-sre.org/)
- [Unity IL2CPP Reverse Engineering](https://github.com/Perfare/Il2CppDumper)
- [Android APK Structure](https://developer.android.com/guide/components/fundamentals)