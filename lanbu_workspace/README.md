# LanBu APK Workspace

This workspace contains all the tools and extracted content for modifying the LanBu APK.

## Structure

- `original/` - Original APK files
- `extracted/` - Extracted APK contents (ZIP extraction)
- `decompiled/` - Decompiled source code (when tools are available)
- `modified/` - Modified files for rebuilding
- `tools/` - Analysis and build scripts

## Usage

### Analyze Components
```bash
cd tools/
./analyze_dex.sh        # Analyze Java/Kotlin code
./analyze_native.sh     # Analyze native libraries
./analyze_unity.sh      # Analyze Unity components
./analyze_firebase.sh   # Analyze Firebase configuration
```

### Make Modifications
1. Copy files from `extracted/` to `modified/`
2. Edit files in `modified/`
3. Use rebuild script to create new APK

### Rebuild APK
```bash
cd tools/
./rebuild_apk.sh
```

## Key Files for Modification

### Java/Kotlin Code
- `classes.dex`, `classes2.dex`, `classes3.dex`

### Native Libraries
- `lib/arm64-v8a/libgame.so` - Game-specific code
- `lib/arm64-v8a/libil2cpp.so` - Unity IL2CPP runtime

### Resources
- `res/` - Android resources (images, layouts, etc.)
- `AndroidManifest.xml` - App configuration

### Unity Assets
- `assets/bin/Data/data.unity3d` - Main asset bundle
- `assets/bin/Data/boot.config` - Unity configuration

## Notes

- The app uses IL2CPP, making C# code analysis more complex
- Firebase integration may need to be disabled for some modifications
- Native library modification requires advanced reverse engineering skills
