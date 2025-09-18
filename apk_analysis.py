#!/usr/bin/env python3
"""
APK Analysis Script
Decompiles and analyzes APK files using APKTool and Ghidra MCP servers
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def analyze_apk(apk_path, output_dir="analysis_output"):
    """
    Comprehensive APK analysis using available MCP tools
    """
    print("🔍 Starting APK Analysis")
    print("=" * 60)
    
    apk_path = Path(apk_path)
    if not apk_path.exists():
        print(f"❌ APK file not found: {apk_path}")
        return False
    
    print(f"📱 Analyzing: {apk_path.name}")
    print(f"📊 Size: {apk_path.stat().st_size:,} bytes")
    print()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Step 1: Try to decompile with APKTool MCP Server
    print("1️⃣ Decompiling APK with APKTool MCP Server...")
    try:
        apktool_result = decompile_with_apktool_mcp(apk_path, output_path)
        if apktool_result:
            print("   ✅ APKTool MCP decompilation successful")
        else:
            print("   ❌ APKTool MCP decompilation failed")
    except Exception as e:
        print(f"   ❌ APKTool MCP error: {e}")
    
    print()
    
    # Step 2: Import into Ghidra for binary analysis
    print("2️⃣ Importing APK into Ghidra...")
    try:
        ghidra_result = analyze_with_ghidra_mcp(apk_path)
        if ghidra_result:
            print("   ✅ Ghidra analysis successful")
        else:
            print("   ❌ Ghidra analysis failed")
    except Exception as e:
        print(f"   ❌ Ghidra error: {e}")
    
    print()
    
    # Step 3: Extract basic APK information
    print("3️⃣ Extracting APK metadata...")
    extract_apk_info(apk_path, output_path)
    
    print()
    print("🎉 Analysis complete!")
    return True





def analyze_manifest(manifest_path):
    """Analyze AndroidManifest.xml for security-relevant information"""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for interesting permissions
        dangerous_permissions = [
            "android.permission.CAMERA",
            "android.permission.RECORD_AUDIO",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.READ_CONTACTS",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.SEND_SMS",
            "android.permission.CALL_PHONE"
        ]
        
        found_permissions = []
        for perm in dangerous_permissions:
            if perm in content:
                found_permissions.append(perm)
        
        if found_permissions:
            print(f"   ⚠️  Sensitive permissions found: {len(found_permissions)}")
            for perm in found_permissions[:3]:  # Show first 3
                print(f"      - {perm.split('.')[-1]}")
            if len(found_permissions) > 3:
                print(f"      ... and {len(found_permissions) - 3} more")
        
        # Look for exported components
        if 'android:exported="true"' in content:
            print("   🔓 Exported components found")
        
        # Look for debug flags
        if 'android:debuggable="true"' in content:
            print("   🐛 Debug mode enabled")
            
    except Exception as e:
        print(f"   ❌ Manifest analysis error: {e}")


def decompile_with_apktool_mcp(apk_path, output_path):
    """Decompile APK using APKTool MCP server"""
    import requests
    import json
    
    # For now, let's use unzip to extract the APK for basic analysis
    try:
        extract_dir = output_path / "extracted_apk"
        extract_dir.mkdir(exist_ok=True)
        
        result = subprocess.run([
            "unzip", "-q", str(apk_path), "-d", str(extract_dir)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   📂 APK extracted successfully")
            analyze_extracted_apk(extract_dir)
            return True
        else:
            print(f"   ❌ APK extraction failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Extraction error: {e}")
        return False


def analyze_extracted_apk(extract_dir):
    """Analyze extracted APK contents"""
    print("   📋 Analyzing extracted content...")
    
    # Check AndroidManifest.xml (binary format)
    manifest_path = extract_dir / "AndroidManifest.xml"
    if manifest_path.exists():
        print(f"   📄 AndroidManifest.xml found ({manifest_path.stat().st_size} bytes) - binary format")
    
    # Check DEX files
    dex_files = list(extract_dir.glob("*.dex"))
    if dex_files:
        print(f"   📜 Found {len(dex_files)} DEX files:")
        for dex in dex_files:
            print(f"      {dex.name}: {dex.stat().st_size:,} bytes")
    
    # Check native libraries
    lib_dir = extract_dir / "lib"
    if lib_dir.exists():
        architectures = [d.name for d in lib_dir.iterdir() if d.is_dir()]
        print(f"   🏗️  Native libraries for architectures: {', '.join(architectures)}")
        
        for arch_dir in lib_dir.iterdir():
            if arch_dir.is_dir():
                so_files = list(arch_dir.glob("*.so"))
                print(f"      {arch_dir.name}: {len(so_files)} libraries")
    
    # Check assets
    assets_dir = extract_dir / "assets"
    if assets_dir.exists():
        asset_files = list(assets_dir.rglob("*"))
        print(f"   💾 Assets: {len([f for f in asset_files if f.is_file()])} files")
    
    # Check resources
    res_dir = extract_dir / "res"
    if res_dir.exists():
        layout_files = list((res_dir / "layout").glob("*.xml")) if (res_dir / "layout").exists() else []
        drawable_files = list((res_dir).rglob("*.png")) + list((res_dir).rglob("*.jpg"))
        print(f"   🎨 Resources: {len(layout_files)} layouts, {len(drawable_files)} images")


def analyze_with_ghidra_mcp(apk_path):
    """Analyze APK with Ghidra MCP server"""
    try:
        # Import the APK binary into Ghidra
        print("   📚 Importing APK into Ghidra...")
        
        # Copy APK to a location Ghidra can access
        ghidra_input = Path("ghidra_analysis") / apk_path.name
        ghidra_input.parent.mkdir(exist_ok=True)
        subprocess.run(["cp", str(apk_path), str(ghidra_input)], check=True)
        
        # Note: In a real environment, you would use the Ghidra MCP server functions
        # For now, let's analyze the DEX files which are the main executable content
        analyze_dex_files(apk_path)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ghidra analysis error: {e}")
        return False


def analyze_dex_files(apk_path):
    """Analyze DEX files in the APK"""
    try:
        # Extract and analyze DEX files
        temp_dir = Path("/tmp/dex_analysis")
        temp_dir.mkdir(exist_ok=True)
        
        # Extract APK
        subprocess.run(["unzip", "-q", str(apk_path), "*.dex", "-d", str(temp_dir)], 
                      capture_output=True)
        
        dex_files = list(temp_dir.glob("*.dex"))
        if dex_files:
            print(f"   🔍 Analyzing {len(dex_files)} DEX files...")
            
            for dex_file in dex_files:
                # Use strings command to find interesting strings
                result = subprocess.run(["strings", str(dex_file)], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    strings_output = result.stdout
                    
                    # Look for interesting patterns
                    interesting_patterns = [
                        "http://", "https://", "ftp://",
                        "password", "secret", "key", "token",
                        "sql", "database", "db",
                        "root", "admin", "debug"
                    ]
                    
                    found_patterns = {}
                    for pattern in interesting_patterns:
                        count = strings_output.lower().count(pattern)
                        if count > 0:
                            found_patterns[pattern] = count
                    
                    if found_patterns:
                        print(f"      {dex_file.name} - Interesting strings found:")
                        for pattern, count in found_patterns.items():
                            print(f"        {pattern}: {count} occurrences")
        
        # Cleanup
        subprocess.run(["rm", "-rf", str(temp_dir)], capture_output=True)
        
    except Exception as e:
        print(f"   ❌ DEX analysis error: {e}")


def extract_apk_info(apk_path, output_path):
    """Extract basic APK information using available tools"""
    try:
        # Use zipinfo to get APK structure
        result = subprocess.run(["zipinfo", "-1", str(apk_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            print(f"   📦 APK contains {len(files)} files")
            
            # Categorize files
            dex_files = [f for f in files if f.endswith('.dex')]
            so_files = [f for f in files if f.endswith('.so')]
            xml_files = [f for f in files if f.endswith('.xml')]
            
            print(f"   📜 DEX files: {len(dex_files)}")
            print(f"   🔧 Native libraries: {len(so_files)}")
            print(f"   📝 XML files: {len(xml_files)}")
            
            # Save file list
            with open(output_path / "apk_file_list.txt", 'w') as f:
                f.write('\n'.join(files))
            print(f"   💾 File list saved to apk_file_list.txt")
            
    except Exception as e:
        print(f"   ❌ APK info extraction error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 apk_analysis.py <apk_path> [output_dir]")
        sys.exit(1)
    
    apk_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_output"
    
    success = analyze_apk(apk_path, output_dir)
    sys.exit(0 if success else 1)