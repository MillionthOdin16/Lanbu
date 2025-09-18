# LanBu APK Analysis and Setup

## Overview

This document provides a comprehensive analysis of the LanBu APK (`com.Glowbeast.LanBu v0.53.apk`) and setup instructions for modifying and developing with the app.

## APK Information

- **Package Name**: `com.Glowbeast.LanBu`
- **App Name**: LanBu
- **Version**: 0.53
- **Developer**: Glowbeast
- **File Size**: ~34 MB
- **Architecture**: ARM64-v8a (64-bit)

## Technology Stack

### Core Framework
- **Unity Engine**: This is a Unity-based Android game
- **IL2CPP**: Uses Unity's IL2CPP scripting backend for performance
- **C# Scripts**: Game logic written in C# (compiled to native code via IL2CPP)

### Key Libraries and Components

#### Unity Engine Files
- `libunity.so` (14.5 MB) - Core Unity engine
- `libil2cpp.so` (49.5 MB) - IL2CPP runtime (largest component)
- `libgame.so` (142 KB) - Game-specific native code
- `libmain.so` (6.7 KB) - Main entry point

#### Firebase Integration
- **Firebase Analytics**: `libFirebaseCppAnalytics.so`
- **Firebase Core**: `libFirebaseCppApp-12_8_0.so`
- **Project ID**: `lanbu-43608`
- **API Key**: `AIzaSyAnAqhR2abrLhmyMYDLYpQUgXQeR1EoqIQ`

#### Additional Components
- **VoxelBusters Essential Kit**: Cross-platform native functionality
- **Google Play Services**: Ads, measurement, location services
- **AndroidX Libraries**: Modern Android components
- **Kotlin Coroutines**: Asynchronous programming support

## File Structure Analysis

### Compiled Code
```
classes.dex     (8.6 MB) - Primary Java/Kotlin code
classes2.dex    (8.1 MB) - Additional Java/Kotlin code  
classes3.dex    (3.6 KB) - Additional Java/Kotlin code
```

### Native Libraries (ARM64)
```
lib/arm64-v8a/
├── libFirebaseCppAnalytics.so    (39 KB)
├── libFirebaseCppApp-12_8_0.so   (4.3 MB)
├── libc++_shared.so              (1.3 MB)
├── libgame.so                    (142 KB)
├── libil2cpp.so                  (49.5 MB)
├── libmain.so                    (6.7 KB)
└── libunity.so                   (14.5 MB)
```

### Unity Assets
```
assets/bin/Data/
├── boot.config                 - Unity boot configuration
├── data.unity3d               - Main Unity asset bundle (2 MB)
├── RuntimeInitializeOnLoads.json - Initialization scripts
├── ScriptingAssemblies.json   - Assembly references
├── unity_app_guid             - Unique app identifier
├── Managed/
│   ├── Metadata/global-metadata.dat - IL2CPP metadata
│   └── Resources/             - .NET resources
└── Resources/
    └── unity default resources - Unity built-in resources
```

### Key Configuration Files
- `AndroidManifest.xml` - App permissions and configuration (binary XML)
- `google-services-desktop.json` - Firebase configuration
- `resources.arsc` - Android resource table

## Unity Project Analysis

### Runtime Initialization
The app uses these key initialization classes:
- **VoxelBusters.CoreLibrary.Helpers**: Core library services
- **VoxelBusters.EssentialKit**: Native platform integration
- **Unity.VisualScripting**: Visual scripting runtime

### Graphics Configuration
```
gfx-disable-mt-rendering=1
gfx-enable-gfx-jobs=1
gfx-enable-native-gfx-jobs=1
gfx-threading-mode=4
androidStartInFullscreen=0
androidRenderOutsideSafeArea=1
```

## Development Setup Instructions

### Prerequisites
The repository includes a Docker-based development environment with:
- APKTool for decompilation/recompilation
- Ghidra for binary analysis
- Uber APK Signer for re-signing
- Java 21 and Python 3.11

### Quick Start

1. **Extract APK Contents** (Already completed):
   ```bash
   mkdir lanbu_extracted
   unzip "com.Glowbeast.LanBu v0.53.apk" -d lanbu_extracted/
   ```

2. **Analyze Native Libraries**:
   - Primary analysis target: `libgame.so` (game-specific code)
   - Secondary targets: `libil2cpp.so` (for understanding game logic)

3. **Analyze DEX Files**:
   - Use tools like `jadx` or `dex2jar` to decompile Java/Kotlin code
   - Focus on `classes.dex` and `classes2.dex` for main app logic

4. **Modify Resources**:
   - Android resources in `res/` directory
   - Unity assets in `assets/bin/Data/`

### Key Areas for Modification

#### 1. Game Logic
- **Location**: `libgame.so` and IL2CPP metadata
- **Tools**: Ghidra, IL2CPP dumper tools
- **Difficulty**: High (requires reverse engineering)

#### 2. UI/Resources
- **Location**: `res/` directory
- **Tools**: APKTool, image editors
- **Difficulty**: Low-Medium

#### 3. Java/Kotlin Code
- **Location**: `classes.dex` files
- **Tools**: jadx, dex2jar, smali/baksmali
- **Difficulty**: Medium

#### 4. Unity Assets
- **Location**: `assets/bin/Data/data.unity3d`
- **Tools**: Unity Asset Bundle Extractor, AssetStudio
- **Difficulty**: Medium-High

### Security Considerations

- App uses certificate pinning (check Firebase configuration)
- IL2CPP obfuscation makes reverse engineering challenging
- Native code analysis required for core game mechanics

### Next Steps

1. Set up proper APKTool decompilation (resolve MCP server path issues)
2. Import native libraries into Ghidra for analysis
3. Decompile DEX files to understand Java/Kotlin logic
4. Analyze Unity asset bundles
5. Create modification workflow and re-signing process

## Tools and Resources

- **APKTool**: For decompiling/recompiling APK
- **Ghidra**: For native library analysis
- **jadx**: For DEX file decompilation
- **Unity Asset Bundle Extractor**: For Unity assets
- **Uber APK Signer**: For re-signing modified APKs

## Firebase Configuration

The app connects to Firebase project `lanbu-43608` with analytics and other services enabled. Modifications may require updating Firebase configuration or disabling certain features.