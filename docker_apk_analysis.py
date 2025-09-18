#!/usr/bin/env python3
"""
Docker-Ready APK Analysis Workflow
This script provides APK analysis that works both locally and in Docker containers
with proper volume mounting for APK accessibility.
"""

import os
import sys
import subprocess
from pathlib import Path


def find_apk_files(search_paths):
    """Find APK files in the given search paths"""
    apk_files = []
    
    for search_path in search_paths:
        path = Path(search_path)
        if path.exists():
            # Look for APK files
            apk_files.extend(path.glob("*.apk"))
            # Also check subdirectories
            for subdir in path.iterdir():
                if subdir.is_dir():
                    apk_files.extend(subdir.glob("*.apk"))
    
    return apk_files


def main():
    print("🐳 Docker-Ready APK Analysis Workflow")
    print("=" * 60)
    
    # Check if we're running in Docker
    in_docker = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER") == "true"
    workspace = os.environ.get("APK_ANALYSIS_WORKSPACE", "/workspace" if in_docker else ".")
    
    if in_docker:
        print("🐳 Running inside Docker container")
        print(f"📁 Workspace: {workspace}")
    else:
        print("💻 Running on local system")
        print(f"📁 Working directory: {os.getcwd()}")
    
    print()
    
    # Search for APK files
    search_paths = [
        workspace,
        ".",
        "/workspace",  # Default Docker workspace
        os.getcwd()   # Current directory
    ]
    
    print("🔍 Searching for APK files...")
    apk_files = find_apk_files(search_paths)
    
    if not apk_files:
        print("❌ No APK files found!")
        print("💡 If running in Docker, ensure APK is volume-mounted:")
        print("   docker run -v /path/to/your/apk:/workspace lanbu apk-analysis")
        print("💡 If running locally, place APK in current directory")
        return False
    
    print(f"📱 Found {len(apk_files)} APK file(s):")
    for i, apk in enumerate(apk_files, 1):
        print(f"   {i}. {apk.name} ({apk.stat().st_size:,} bytes)")
    
    # Use the first APK file found
    apk_file = apk_files[0]
    print(f"\n🎯 Analyzing: {apk_file.name}")
    
    # Create output directory
    output_dir = Path(workspace) / "analysis_results"
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    print()
    
    # Run analysis workflows
    analysis_results = {}
    
    # 1. Basic analysis
    print("1️⃣ Running basic APK analysis...")
    try:
        result = run_basic_analysis(apk_file, output_dir)
        analysis_results["basic"] = result
        print("   ✅ Basic analysis completed")
    except Exception as e:
        print(f"   ❌ Basic analysis failed: {e}")
        analysis_results["basic"] = False
    
    # 2. Security analysis
    print("\n2️⃣ Running security analysis...")
    try:
        result = run_security_analysis(apk_file, output_dir)
        analysis_results["security"] = result
        print("   ✅ Security analysis completed")
    except Exception as e:
        print(f"   ❌ Security analysis failed: {e}")
        analysis_results["security"] = False
    
    # 3. Generate summary report
    print("\n3️⃣ Generating summary report...")
    try:
        generate_summary_report(apk_file, output_dir, analysis_results)
        print("   ✅ Summary report generated")
    except Exception as e:
        print(f"   ❌ Report generation failed: {e}")
    
    print()
    print("🎉 APK Analysis Complete!")
    print(f"📊 Results available in: {output_dir}")
    
    # List generated files
    result_files = list(output_dir.glob("*"))
    if result_files:
        print("\n📄 Generated files:")
        for file in result_files:
            if file.is_file():
                print(f"   - {file.name} ({file.stat().st_size:,} bytes)")
    
    return any(analysis_results.values())


def run_basic_analysis(apk_file, output_dir):
    """Run basic APK structure analysis"""
    try:
        # Extract APK contents
        extract_dir = output_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        result = subprocess.run([
            "unzip", "-q", str(apk_file), "-d", str(extract_dir)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return False
        
        # Get file listing
        files_result = subprocess.run([
            "zipinfo", "-1", str(apk_file)
        ], capture_output=True, text=True)
        
        if files_result.returncode == 0:
            with open(output_dir / "file_listing.txt", "w") as f:
                f.write(files_result.stdout)
        
        # Analyze DEX files
        dex_files = list(extract_dir.glob("*.dex"))
        dex_info = {}
        
        for dex_file in dex_files:
            dex_info[dex_file.name] = {
                "size": dex_file.stat().st_size,
                "strings": analyze_dex_strings(dex_file)
            }
        
        # Save DEX analysis
        import json
        with open(output_dir / "dex_analysis.json", "w") as f:
            json.dump(dex_info, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Basic analysis error: {e}")
        return False


def analyze_dex_strings(dex_file):
    """Analyze strings in DEX file for security indicators"""
    try:
        result = subprocess.run(["strings", str(dex_file)], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            return {}
        
        content = result.stdout.lower()
        patterns = {
            'network': ['http://', 'https://', 'socket', 'tcp'],
            'crypto': ['encrypt', 'decrypt', 'cipher', 'hash'],
            'auth': ['password', 'token', 'secret', 'key'],
            'database': ['sql', 'sqlite', 'database', 'select'],
            'debug': ['debug', 'log', 'test', 'verbose']
        }
        
        results = {}
        for category, terms in patterns.items():
            count = sum(content.count(term) for term in terms)
            if count > 0:
                results[category] = count
        
        return results
        
    except Exception:
        return {}


def run_security_analysis(apk_file, output_dir):
    """Run security-focused analysis"""
    try:
        security_report = []
        security_report.append("# APK Security Analysis Report")
        security_report.append(f"**APK:** {apk_file.name}")
        security_report.append(f"**Size:** {apk_file.stat().st_size:,} bytes")
        security_report.append("")
        
        # Check for debug indicators
        extract_dir = output_dir / "extracted"
        if extract_dir.exists():
            # Look for debug indicators in DEX files
            debug_found = False
            dex_files = list(extract_dir.glob("*.dex"))
            
            for dex_file in dex_files:
                try:
                    result = subprocess.run(["strings", str(dex_file)], 
                                          capture_output=True, text=True)
                    if "debuggable" in result.stdout.lower():
                        debug_found = True
                        break
                except:
                    pass
            
            if debug_found:
                security_report.append("⚠️ **Debug mode indicators found**")
            
            # Check for native libraries
            lib_dir = extract_dir / "lib"
            if lib_dir.exists():
                arch_dirs = [d.name for d in lib_dir.iterdir() if d.is_dir()]
                security_report.append(f"🏗️ **Native libraries:** {', '.join(arch_dirs)}")
            
            # Check for sensitive permissions (would need manifest parsing)
            security_report.append("ℹ️ **Note:** Full permission analysis requires AndroidManifest.xml parsing")
        
        security_report.append("")
        security_report.append("## Recommendations")
        security_report.append("- Implement code obfuscation")
        security_report.append("- Use certificate pinning for network security")
        security_report.append("- Add root detection mechanisms")
        security_report.append("- Regular security testing")
        
        # Save security report
        with open(output_dir / "security_report.md", "w") as f:
            f.write("\n".join(security_report))
        
        return True
        
    except Exception as e:
        print(f"Security analysis error: {e}")
        return False


def generate_summary_report(apk_file, output_dir, analysis_results):
    """Generate a summary report of all analyses"""
    summary = []
    summary.append("# APK Analysis Summary")
    summary.append(f"**APK File:** {apk_file.name}")
    summary.append(f"**Analysis Date:** {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
    summary.append("")
    
    summary.append("## Analysis Results")
    for analysis_type, success in analysis_results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        summary.append(f"- {analysis_type.title()} Analysis: {status}")
    
    summary.append("")
    summary.append("## Generated Files")
    
    result_files = [f for f in output_dir.glob("*") if f.is_file()]
    for file in result_files:
        summary.append(f"- `{file.name}` ({file.stat().st_size:,} bytes)")
    
    summary.append("")
    summary.append("---")
    summary.append("*Generated by Docker-Ready APK Analysis Workflow*")
    
    with open(output_dir / "SUMMARY.md", "w") as f:
        f.write("\n".join(summary))


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)