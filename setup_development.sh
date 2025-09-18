#!/bin/bash

# LanBu APK Development Setup Script
# This script sets up the development environment for modifying the LanBu APK

set -e

echo "🚀 Setting up LanBu APK development environment..."

# Define paths
APK_FILE="com.Glowbeast.LanBu v0.53.apk"
EXTRACTED_DIR="lanbu_extracted"
DECOMPILED_DIR="lanbu_decompiled"
WORKSPACE_DIR="lanbu_workspace"

# Create workspace structure
echo "📁 Creating workspace structure..."
mkdir -p "$WORKSPACE_DIR"/{original,extracted,decompiled,modified,tools}

# Copy original APK
echo "📦 Copying original APK..."
cp "$APK_FILE" "$WORKSPACE_DIR/original/"
cp "$APK_FILE" "$WORKSPACE_DIR/original/lanbu.apk"

# Extract APK contents (already done, but ensure it's in workspace)
echo "📂 Setting up extracted APK contents..."
if [ -d "$EXTRACTED_DIR" ]; then
    cp -r "$EXTRACTED_DIR" "$WORKSPACE_DIR/extracted/"
else
    echo "⚠️  Extracted directory not found. Extracting APK..."
    mkdir -p "$WORKSPACE_DIR/extracted"
    cd "$WORKSPACE_DIR/extracted"
    unzip "../../$APK_FILE"
    cd ../..
fi

# Create tools directory with useful scripts
echo "🔧 Setting up development tools..."

# Create DEX analysis script
cat > "$WORKSPACE_DIR/tools/analyze_dex.sh" << 'EOF'
#!/bin/bash
# Analyze DEX files using available tools

echo "🔍 Analyzing DEX files..."

if command -v jadx &> /dev/null; then
    echo "Using jadx for DEX decompilation..."
    jadx -d ../decompiled/java ../extracted/classes.dex
    jadx -d ../decompiled/java2 ../extracted/classes2.dex
    jadx -d ../decompiled/java3 ../extracted/classes3.dex
elif command -v dex2jar &> /dev/null; then
    echo "Using dex2jar for DEX conversion..."
    dex2jar ../extracted/classes.dex -o ../decompiled/classes.jar
    dex2jar ../extracted/classes2.dex -o ../decompiled/classes2.jar
    dex2jar ../extracted/classes3.dex -o ../decompiled/classes3.jar
else
    echo "⚠️  No DEX analysis tools found. Install jadx or dex2jar."
fi
EOF

# Create native library analysis script
cat > "$WORKSPACE_DIR/tools/analyze_native.sh" << 'EOF'
#!/bin/bash
# Analyze native libraries

echo "🔍 Analyzing native libraries..."

cd "../extracted/lib/arm64-v8a"

echo "📊 Library information:"
for lib in *.so; do
    echo "--- $lib ---"
    file "$lib"
    size=$(stat -f%z "$lib" 2>/dev/null || stat -c%s "$lib" 2>/dev/null || echo "unknown")
    echo "Size: $size bytes"
    
    # Check for symbols
    if command -v nm &> /dev/null; then
        echo "Symbols:"
        nm -D "$lib" 2>/dev/null | head -10 || echo "No symbols found"
    fi
    
    # Check for strings
    if command -v strings &> /dev/null; then
        echo "Interesting strings:"
        strings "$lib" | grep -E "(unity|game|lan|bu)" | head -5 || echo "No relevant strings found"
    fi
    echo
done
EOF

# Create APK rebuild script
cat > "$WORKSPACE_DIR/tools/rebuild_apk.sh" << 'EOF'
#!/bin/bash
# Rebuild APK after modifications

echo "🔨 Rebuilding APK..."

# This would use apktool when the MCP server path issues are resolved
echo "⚠️  APKTool MCP server needs path resolution"
echo "Manual steps:"
echo "1. Use apktool to decompile: apktool d original/lanbu.apk -o decompiled/"
echo "2. Make modifications in decompiled/ directory"
echo "3. Rebuild: apktool b decompiled/ -o modified/lanbu_modified.apk"
echo "4. Sign: uber-apk-signer --apks modified/lanbu_modified.apk"

# Alternative approach using zip
echo "📦 Alternative: Manual ZIP approach"
echo "You can modify files in extracted/ and rezip as APK"
EOF

# Create Unity asset analysis script
cat > "$WORKSPACE_DIR/tools/analyze_unity.sh" << 'EOF'
#!/bin/bash
# Analyze Unity-specific components

echo "🎮 Analyzing Unity components..."

cd "../extracted"

echo "📋 Unity configuration:"
echo "--- boot.config ---"
cat assets/bin/Data/boot.config 2>/dev/null || echo "File not found"
echo

echo "📋 Unity app GUID:"
cat assets/bin/Data/unity_app_guid 2>/dev/null || echo "File not found"
echo

echo "📋 Runtime initialization:"
cat assets/bin/Data/RuntimeInitializeOnLoads.json 2>/dev/null | jq . || echo "File not found or invalid JSON"
echo

echo "📋 Scripting assemblies:"
cat assets/bin/Data/ScriptingAssemblies.json 2>/dev/null | jq . || echo "File not found or invalid JSON"
echo

echo "📊 Asset sizes:"
ls -lh assets/bin/Data/ | grep -E "\.(unity3d|dat|json)$"
EOF

# Create Firebase analysis script
cat > "$WORKSPACE_DIR/tools/analyze_firebase.sh" << 'EOF'
#!/bin/bash
# Analyze Firebase configuration

echo "🔥 Analyzing Firebase configuration..."

cd "../extracted"

echo "📋 Firebase configuration:"
cat assets/google-services-desktop.json 2>/dev/null | jq . || echo "File not found"
echo

echo "📋 Firebase properties files:"
find . -name "*firebase*" -type f | while read file; do
    echo "--- $file ---"
    cat "$file"
    echo
done
EOF

# Make scripts executable
chmod +x "$WORKSPACE_DIR/tools/"*.sh

# Create workspace README
cat > "$WORKSPACE_DIR/README.md" << 'EOF'
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
EOF

# Create analysis summary
echo "📊 Generating initial analysis summary..."
cat > "$WORKSPACE_DIR/ANALYSIS_SUMMARY.md" << EOF
# LanBu APK Analysis Summary

Generated on: $(date)

## File Statistics

### APK Size
$(ls -lh "$APK_FILE" | awk '{print $5}')

### Major Components
- Classes DEX: $(ls -lh "$WORKSPACE_DIR/extracted/classes"*.dex | awk '{sum+=$5} END {print sum/1024/1024 " MB"}')
- Native Libraries: $(ls -lh "$WORKSPACE_DIR/extracted/lib/arm64-v8a/"*.so | awk '{sum+=$5} END {print sum/1024/1024 " MB"}')
- Unity Assets: $(ls -lh "$WORKSPACE_DIR/extracted/assets/bin/Data/data.unity3d" | awk '{print $5}')
- Resources: $(ls -lh "$WORKSPACE_DIR/extracted/resources.arsc" | awk '{print $5}')

### Package Information
- Package: $(grep -o 'com\.Glowbeast\.LanBu' "$WORKSPACE_DIR/extracted/assets/google-services-desktop.json" || echo "com.Glowbeast.LanBu")
- Firebase Project: $(grep -o '"project_id": "[^"]*"' "$WORKSPACE_DIR/extracted/assets/google-services-desktop.json" | cut -d'"' -f4 || echo "lanbu-43608")

### Native Libraries
$(cd "$WORKSPACE_DIR/extracted/lib/arm64-v8a" && ls -1 *.so | while read lib; do echo "- $lib ($(stat -c%s "$lib" | numfmt --to=iec-i)B)"; done)

## Recommended Next Steps

1. **Install analysis tools**: jadx, dex2jar, ghidra
2. **Run analysis scripts** in tools/ directory
3. **Focus areas**:
   - libgame.so for game-specific modifications
   - classes.dex for Java/Kotlin UI and logic
   - Unity assets for game content
   - AndroidManifest.xml for permissions and configuration

## Development Status

✅ APK extracted and analyzed
✅ Workspace structure created
✅ Analysis scripts prepared
⚠️  APKTool MCP server path issues (needs resolution)
⚠️  Ghidra import path issues (needs resolution)
⏳ DEX decompilation (requires tools installation)
⏳ Native library analysis (requires tools installation)
EOF

echo "✅ Workspace setup complete!"
echo
echo "📁 Workspace created at: $WORKSPACE_DIR"
echo "📖 See $WORKSPACE_DIR/README.md for usage instructions"
echo "📊 See $WORKSPACE_DIR/ANALYSIS_SUMMARY.md for current analysis"
echo
echo "🔧 Next steps:"
echo "1. Install analysis tools (jadx, ghidra, etc.)"
echo "2. Run analysis scripts in $WORKSPACE_DIR/tools/"
echo "3. Resolve MCP server path issues for automated tooling"
echo "4. Begin modifications based on analysis results"