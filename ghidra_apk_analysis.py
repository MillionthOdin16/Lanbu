#!/usr/bin/env python3
"""
APK Analysis with Ghidra Integration
Uses Ghidra MCP server to perform deep binary analysis of APK files
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def analyze_apk_with_ghidra(apk_path):
    """Analyze APK using Ghidra MCP server"""
    print("🔍 APK Analysis with Ghidra")
    print("=" * 50)
    
    apk_path = Path(apk_path)
    if not apk_path.exists():
        print(f"❌ APK file not found: {apk_path}")
        return False
    
    print(f"📱 Analyzing: {apk_path.name}")
    print(f"📊 Size: {apk_path.stat().st_size:,} bytes")
    print()
    
    # Step 1: Check Ghidra server health
    print("1️⃣ Checking Ghidra server status...")
    try:
        from functions import ghidra_analyzer
        binaries = ghidra_analyzer.list_project_binaries()
        print(f"   ✅ Ghidra server responsive")
        print(f"   📚 Current project has {len(binaries.get('programs', []))} binaries")
    except Exception as e:
        print(f"   ❌ Ghidra server error: {e}")
        return False
    
    print()
    
    # Step 2: Import APK into Ghidra
    print("2️⃣ Importing APK into Ghidra...")
    try:
        # Copy APK to a location accessible by Ghidra
        ghidra_apk_path = f"apk_analysis_{apk_path.stem}.apk"
        subprocess.run(["cp", str(apk_path), ghidra_apk_path], check=True)
        
        # Import the APK binary
        result = ghidra_analyzer.import_binary(ghidra_apk_path)
        if result:
            print("   ✅ APK imported successfully")
        else:
            print("   ⚠️ APK import completed with warnings")
            
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    print()
    
    # Step 3: List imported binaries
    print("3️⃣ Analyzing imported binaries...")
    try:
        binaries = ghidra_analyzer.list_project_binaries()
        programs = binaries.get('programs', [])
        
        if programs:
            print(f"   📚 Found {len(programs)} binaries:")
            for program in programs:
                print(f"      - {program}")
                
                # Analyze this binary
                analyze_binary_with_ghidra(program)
        else:
            print("   ⚠️ No binaries found in Ghidra project")
            
    except Exception as e:
        print(f"   ❌ Binary analysis failed: {e}")
    
    print()
    
    # Step 4: Search for interesting functions
    print("4️⃣ Searching for security-relevant functions...")
    try:
        security_searches = [
            "encrypt", "decrypt", "password", "token", "auth",
            "socket", "network", "http", "ssl", "crypto"
        ]
        
        for search_term in security_searches:
            try:
                results = ghidra_analyzer.search_functions_by_name(
                    ghidra_apk_path, search_term, limit=5
                )
                if results and len(results) > 0:
                    print(f"   🔍 '{search_term}': {len(results)} matches")
            except:
                pass  # Search term might not be found
                
    except Exception as e:
        print(f"   ❌ Function search failed: {e}")
    
    print()
    
    # Step 5: Perform semantic code search
    print("5️⃣ Performing semantic code analysis...")
    try:
        semantic_queries = [
            "function main",
            "encryption algorithm",
            "network communication",
            "file operations",
            "database access"
        ]
        
        for query in semantic_queries:
            try:
                results = ghidra_analyzer.search_code(ghidra_apk_path, query, limit=3)
                if results:
                    print(f"   🧠 '{query}': Found relevant code")
            except:
                pass  # Query might not return results
                
    except Exception as e:
        print(f"   ❌ Semantic search failed: {e}")
    
    print()
    print("🎉 Ghidra analysis complete!")
    return True


def analyze_binary_with_ghidra(binary_name):
    """Analyze a specific binary with Ghidra"""
    try:
        from functions import ghidra_analyzer
        
        # Search for symbols
        symbols = ghidra_analyzer.search_symbols_by_name(binary_name, "main", limit=5)
        if symbols:
            print(f"         📝 Found symbols containing 'main'")
        
        # Look for cross-references
        try:
            xrefs = ghidra_analyzer.list_cross_references(binary_name, "main")
            if xrefs:
                print(f"         🔗 Found cross-references to 'main'")
        except:
            pass  # main might not exist
        
    except Exception as e:
        print(f"         ❌ Binary analysis error: {e}")


def extract_and_analyze_dex_files(apk_path):
    """Extract DEX files and analyze them separately"""
    print("6️⃣ Analyzing DEX files separately...")
    
    try:
        # Create temporary directory
        temp_dir = Path("/tmp/dex_ghidra_analysis")
        temp_dir.mkdir(exist_ok=True)
        
        # Extract DEX files
        result = subprocess.run([
            "unzip", "-q", str(apk_path), "*.dex", "-d", str(temp_dir)
        ], capture_output=True)
        
        dex_files = list(temp_dir.glob("*.dex"))
        
        if dex_files:
            print(f"   📜 Extracted {len(dex_files)} DEX files")
            
            for dex_file in dex_files:
                print(f"   🔍 Analyzing {dex_file.name}...")
                try:
                    from functions import ghidra_analyzer
                    
                    # Import DEX file into Ghidra
                    result = ghidra_analyzer.import_binary(str(dex_file))
                    if result:
                        print(f"      ✅ {dex_file.name} imported")
                        
                        # Search for interesting functions in this DEX
                        functions = ghidra_analyzer.search_functions_by_name(
                            dex_file.name, "onCreate", limit=3
                        )
                        if functions:
                            print(f"      📱 Found Android lifecycle functions")
                    
                except Exception as e:
                    print(f"      ❌ Analysis failed: {e}")
        
        # Cleanup
        subprocess.run(["rm", "-rf", str(temp_dir)], capture_output=True)
        
    except Exception as e:
        print(f"   ❌ DEX analysis failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ghidra_apk_analysis.py <apk_path>")
        sys.exit(1)
    
    apk_path = sys.argv[1]
    success = analyze_apk_with_ghidra(apk_path)
    
    # Also analyze DEX files separately
    extract_and_analyze_dex_files(apk_path)
    
    sys.exit(0 if success else 1)