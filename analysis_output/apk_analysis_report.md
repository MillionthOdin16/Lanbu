# APK Analysis Report: Lanbu v0.53

## Overview
- **APK Name**: lanbu.apk (com.Glowbeast.LanBu v0.53.apk)
- **File Size**: 34,055,115 bytes (33 MB)
- **Analysis Date**: September 18, 2025

## APK Structure Analysis

### DEX Files (Compiled Code)
```
classes.dex     - 8.2MB (Main application code)
classes2.dex    - 7.7MB (Additional application code)  
classes3.dex    - 3.6KB (Minimal additional code)
```

### Native Libraries (ARM64 Architecture)
Located in `lib/arm64-v8a/`:
```
libFirebaseCppAnalytics.so  - Firebase Analytics
libFirebaseCppApp-12_8_0.so - Firebase Core App
libgame.so                  - Main game logic
libc++_shared.so           - C++ Standard Library
libunity.so                - Unity Engine
libmain.so                 - Main application entry
libil2cpp.so               - IL2CPP Runtime (Unity)
```

### Key Technologies Identified
1. **Unity Game Engine** - This is a Unity-based mobile game
2. **Firebase Integration** - Analytics and core services
3. **IL2CPP** - Unity's C++ code generation backend
4. **Google Play Services** - Ads, measurement, location services

## Firebase & Google Services Integration

The APK includes extensive Firebase and Google Play Services:
- Firebase Analytics
- Firebase Installations  
- Firebase Measurement/Metrics
- Google Play Services Ads
- Google Play Services Location
- Google Play Services Measurement
- Google Play Services Places

## Assets Analysis

### Unity Asset Structure
The `assets/bin/Data/` directory contains typical Unity game assets:
- `data.unity3d` - Main game data
- `global-metadata.dat` - IL2CPP metadata
- `RuntimeInitializeOnLoads.json` - Unity initialization
- `ScriptingAssemblies.json` - Assembly information
- Unity default resources

### Configuration Files
Multiple `.properties` files for various services:
- Firebase configuration
- Google Play Services configuration  
- Transport and measurement settings
- Billing properties

## Security Analysis

### Certificate Information
- **Issuer**: Android Debug Certificate (C=US, O=Android, CN=Android Debug)
- **Validity**: August 12, 2024 - December 29, 2051
- **Certificate Type**: Debug certificate (indicates development/testing build)

### AndroidX Library Versions
The app uses modern AndroidX libraries:
- Core libraries: 1.9.0
- AppCompat: 1.6.1
- Fragment: 1.3.6
- Room database: 2.2.5
- Work manager: 2.7.0
- Privacy sandbox ads: 1.1.0-beta11

### Unity Build Information
- **Unity App GUID**: 3a9b0f74-fd04-47d6-9bbf-9301742522e9
- **Build GUID**: 818bcc2e60ae4899816faa8f20a82e7b
- **Graphics Configuration**: Multi-threaded rendering enabled, GFX jobs enabled
- **Platform**: Android fullscreen disabled, safe area rendering enabled

### Permissions (from AndroidManifest.xml - Binary Format)
The AndroidManifest.xml is in binary format (26,840 bytes). Key indicators from file structure suggest:
- Extensive permission usage (large manifest size)
- Multiple service declarations
- Firebase and Google Play Services integration

### String Analysis Highlights
From DEX file analysis, found references to:
- HTTP/HTTPS URLs (Google services, AdMob)
- Firebase configuration endpoints
- Unity-related strings and configurations
- Google Play Services APIs
- Location services integration
- Billing and monetization features

### Network Indicators
- Multiple Google/Firebase service endpoints
- AdMob advertising URLs (https://goo.gle/admob-android-update-manifest)
- Firebase measurement and analytics endpoints
- Ad Manager integration

## Application Type Assessment
This appears to be a **Unity-based mobile game** with:
- Extensive analytics and measurement capabilities
- Advertising integration (AdMob)
- Firebase backend services
- Location services integration
- Billing/monetization features

## Recommendations for Further Analysis

To complete the analysis, the following steps would be beneficial:

1. **Decode AndroidManifest.xml** - Use APKTool to get readable manifest with permissions
2. **Decompile DEX files** - Convert to Java source for code analysis
3. **Resource analysis** - Examine drawable resources, layouts, and strings
4. **Certificate analysis** - Check signing certificates in META-INF
5. **Native library analysis** - Use tools like Ghidra to analyze .so files

## Files for Further Investigation

Key files identified for deeper analysis:
- `AndroidManifest.xml` (binary) - App permissions and configuration
- `classes.dex` and `classes2.dex` - Main application logic
- `assets/bin/Data/global-metadata.dat` - IL2CPP metadata
- `lib/arm64-v8a/libgame.so` - Core game logic
- `META-INF/` directory - Signing certificates

---
*Analysis performed using basic extraction and string analysis techniques.*