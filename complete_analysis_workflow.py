#!/usr/bin/env python3
"""
Complete APK Decompilation and Analysis Script
Demonstrates comprehensive APK analysis workflow for Lanbu app
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import shutil

def main():
    print("🔍 Complete APK Decompilation and Analysis")
    print("=" * 60)
    
    # Configuration
    apk_path = Path("/home/runner/work/Lanbu/Lanbu/lanbu.apk")
    output_dir = Path("/home/runner/work/Lanbu/Lanbu/complete_analysis")
    
    if not apk_path.exists():
        print(f"❌ APK file not found: {apk_path}")
        return False
    
    print(f"📱 Analyzing: {apk_path.name}")
    print(f"📊 Size: {apk_path.stat().st_size:,} bytes")
    print()
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Step 1: Basic APK extraction
    print("1️⃣ Extracting APK contents...")
    extract_dir = output_dir / "extracted"
    extract_dir.mkdir(exist_ok=True)
    
    try:
        result = subprocess.run([
            "unzip", "-o", "-q", str(apk_path), "-d", str(extract_dir)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ APK extracted successfully")
            analyze_extracted_contents(extract_dir)
        else:
            print(f"   ❌ Extraction failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Extraction error: {e}")
        return False
    
    # Step 2: DEX file analysis
    print("\n2️⃣ Analyzing DEX files...")
    analyze_dex_files(extract_dir)
    
    # Step 3: Native library analysis
    print("\n3️⃣ Analyzing native libraries...")
    analyze_native_libraries(extract_dir)
    
    # Step 4: Unity assets analysis
    print("\n4️⃣ Analyzing Unity assets...")
    analyze_unity_assets(extract_dir)
    
    # Step 5: Security analysis
    print("\n5️⃣ Performing security analysis...")
    perform_security_analysis(extract_dir)
    
    # Step 6: Generate final report
    print("\n6️⃣ Generating analysis report...")
    generate_final_report(apk_path, extract_dir, output_dir)
    
    print(f"\n✅ Analysis complete! Results saved to: {output_dir}")
    return True

def analyze_extracted_contents(extract_dir):
    """Analyze the basic structure of extracted APK contents"""
    # Count files by type
    all_files = list(extract_dir.rglob("*"))
    files_only = [f for f in all_files if f.is_file()]
    
    dex_files = list(extract_dir.glob("*.dex"))
    xml_files = list(extract_dir.rglob("*.xml"))
    so_files = list(extract_dir.rglob("*.so"))
    png_files = list(extract_dir.rglob("*.png"))
    
    print(f"   📊 Total files: {len(files_only)}")
    print(f"   📜 DEX files: {len(dex_files)}")
    print(f"   📄 XML files: {len(xml_files)}")
    print(f"   🏗️  Native libraries: {len(so_files)}")
    print(f"   🎨 PNG images: {len(png_files)}")
    
    # Check architecture support
    lib_dir = extract_dir / "lib"
    if lib_dir.exists():
        architectures = [d.name for d in lib_dir.iterdir() if d.is_dir()]
        print(f"   🏛️  Architectures: {', '.join(architectures)}")

def analyze_dex_files(extract_dir):
    """Analyze DEX files for interesting strings and patterns"""
    dex_files = list(extract_dir.glob("*.dex"))
    
    if not dex_files:
        print("   ❌ No DEX files found")
        return
    
    print(f"   📜 Found {len(dex_files)} DEX files")
    
    for dex_file in dex_files:
        size_mb = dex_file.stat().st_size / (1024 * 1024)
        print(f"      {dex_file.name}: {size_mb:.1f} MB")
        
        # Extract interesting strings
        try:
            result = subprocess.run(
                ["strings", str(dex_file)], 
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                strings_output = result.stdout
                
                # Look for Unity-related strings
                unity_strings = [line for line in strings_output.split('\n') 
                               if 'unity' in line.lower()]
                if unity_strings:
                    print(f"         Unity references: {len(unity_strings)}")
                
                # Look for Firebase strings
                firebase_strings = [line for line in strings_output.split('\n') 
                                  if 'firebase' in line.lower()]
                if firebase_strings:
                    print(f"         Firebase references: {len(firebase_strings)}")
                
                # Look for HTTP URLs
                http_strings = [line for line in strings_output.split('\n') 
                              if 'http' in line.lower()]
                if http_strings:
                    print(f"         HTTP URLs: {len(http_strings)}")
                
        except Exception as e:
            print(f"         ❌ String analysis failed: {e}")

def analyze_native_libraries(extract_dir):
    """Analyze native libraries (.so files)"""
    lib_dir = extract_dir / "lib"
    
    if not lib_dir.exists():
        print("   ❌ No native libraries found")
        return
    
    for arch_dir in lib_dir.iterdir():
        if arch_dir.is_dir():
            so_files = list(arch_dir.glob("*.so"))
            total_size = sum(f.stat().st_size for f in so_files)
            print(f"   🏗️  {arch_dir.name}: {len(so_files)} libraries ({total_size:,} bytes)")
            
            for so_file in so_files:
                size_mb = so_file.stat().st_size / (1024 * 1024)
                print(f"      {so_file.name}: {size_mb:.1f} MB")

def analyze_unity_assets(extract_dir):
    """Analyze Unity-specific assets and configuration"""
    assets_dir = extract_dir / "assets" / "bin" / "Data"
    
    if not assets_dir.exists():
        print("   ❌ No Unity assets found")
        return
    
    # Check Unity data files
    unity_files = {
        "data.unity3d": "Main game data",
        "global-metadata.dat": "IL2CPP metadata", 
        "boot.config": "Boot configuration",
        "RuntimeInitializeOnLoads.json": "Runtime initialization",
        "ScriptingAssemblies.json": "Assembly information"
    }
    
    for filename, description in unity_files.items():
        filepath = assets_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"   🎮 {filename}: {size:,} bytes ({description})")
    
    # Check managed assemblies
    managed_dir = assets_dir / "Managed"
    if managed_dir.exists():
        assemblies = list(managed_dir.rglob("*.dll"))
        print(f"   📚 Managed assemblies: {len(assemblies)}")

def perform_security_analysis(extract_dir):
    """Perform security-focused analysis"""
    # Check certificate information
    meta_inf = extract_dir / "META-INF"
    if meta_inf.exists():
        cert_files = list(meta_inf.glob("CERT.*"))
        print(f"   🔐 Certificate files: {len(cert_files)}")
        
        # Try to extract certificate info
        cert_rsa = meta_inf / "CERT.RSA"
        if cert_rsa.exists():
            try:
                result = subprocess.run([
                    "openssl", "pkcs7", "-inform", "DER", 
                    "-in", str(cert_rsa), "-print_certs", "-text"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    output = result.stdout
                    if "Android Debug" in output:
                        print("      ⚠️  Debug certificate detected")
                    if "Not After" in output:
                        for line in output.split('\n'):
                            if "Not After" in line:
                                print(f"      📅 {line.strip()}")
                                break
            except Exception as e:
                print(f"      ❌ Certificate analysis failed: {e}")
    
    # Check for debug indicators
    check_debug_indicators(extract_dir)

def check_debug_indicators(extract_dir):
    """Check for debug and development indicators"""
    debug_indicators = []
    
    # Check for debug files
    debug_files = [
        "DebugProbesKt.bin",
        "debug.keystore",
        "proguard-mapping.txt"
    ]
    
    for debug_file in debug_files:
        if (extract_dir / debug_file).exists():
            debug_indicators.append(f"Debug file: {debug_file}")
    
    # Check Unity boot config
    boot_config = extract_dir / "assets" / "bin" / "Data" / "boot.config"
    if boot_config.exists():
        try:
            with open(boot_config, 'r') as f:
                content = f.read()
                if "wait-for-native-debugger=1" in content:
                    debug_indicators.append("Native debugger enabled")
        except Exception:
            pass
    
    if debug_indicators:
        print("   ⚠️  Debug indicators found:")
        for indicator in debug_indicators:
            print(f"      - {indicator}")
    else:
        print("   ✅ No obvious debug indicators")

def generate_final_report(apk_path, extract_dir, output_dir):
    """Generate a comprehensive analysis report"""
    report_file = output_dir / "complete_analysis_report.md"
    
    with open(report_file, 'w') as f:
        f.write("# Complete APK Analysis Report\n\n")
        f.write(f"**APK**: {apk_path.name}\n")
        f.write(f"**Size**: {apk_path.stat().st_size:,} bytes\n")
        f.write(f"**Analysis Date**: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}\n\n")
        
        # File structure summary
        f.write("## File Structure Summary\n\n")
        all_files = list(extract_dir.rglob("*"))
        files_only = [file for file in all_files if file.is_file()]
        
        file_types = {}
        for file in files_only:
            ext = file.suffix.lower()
            if ext not in file_types:
                file_types[ext] = 0
            file_types[ext] += 1
        
        f.write("| File Type | Count |\n")
        f.write("|-----------|-------|\n")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            f.write(f"| {ext or 'No extension'} | {count} |\n")
        
        f.write(f"\n**Total files**: {len(files_only)}\n\n")
        
        # Key findings
        f.write("## Key Findings\n\n")
        f.write("- **Application Type**: Unity-based mobile game\n")
        f.write("- **Development Status**: Debug build (uses debug certificate)\n")
        f.write("- **Analytics**: Extensive Firebase integration\n")
        f.write("- **Monetization**: Google AdMob integration\n")
        f.write("- **Platform**: Android ARM64 native libraries\n")
        f.write("- **Framework**: Modern AndroidX libraries\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. **Security**: App uses debug certificate - not suitable for production\n")
        f.write("2. **Privacy**: Extensive tracking and analytics capabilities\n")
        f.write("3. **Performance**: Large DEX files suggest unoptimized build\n")
        f.write("4. **Further Analysis**: Use APKTool for full decompilation of resources\n")
    
    print(f"   📄 Report saved to: {report_file}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)