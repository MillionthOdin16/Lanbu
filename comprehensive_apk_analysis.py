#!/usr/bin/env python3
"""
Comprehensive APK Analysis using MCP Tools
This script provides a complete workflow for APK decompilation and security analysis
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 comprehensive_apk_analysis.py <apk_path>")
        sys.exit(1)
    
    apk_path = sys.argv[1]
    
    print("🔒 Comprehensive APK Security Analysis")
    print("=" * 70)
    
    # Run the comprehensive analysis
    analyzer = APKAnalyzer(apk_path)
    success = analyzer.run_full_analysis()
    
    sys.exit(0 if success else 1)


class APKAnalyzer:
    def __init__(self, apk_path):
        self.apk_path = Path(apk_path)
        self.output_dir = Path("comprehensive_analysis_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Create report file
        self.report_file = self.output_dir / "security_analysis_report.md"
        self.report_lines = []
        
        self.add_to_report(f"# APK Security Analysis Report")
        self.add_to_report(f"**APK:** {self.apk_path.name}")
        self.add_to_report(f"**Analysis Date:** {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
        self.add_to_report(f"**APK Size:** {self.apk_path.stat().st_size:,} bytes")
        self.add_to_report("")
        
    def add_to_report(self, line):
        """Add line to analysis report"""
        self.report_lines.append(line)
        print(line.replace("**", "").replace("# ", "🔍 "))
    
    def save_report(self):
        """Save the analysis report"""
        with open(self.report_file, 'w') as f:
            f.write('\n'.join(self.report_lines))
        print(f"\n📄 Analysis report saved to: {self.report_file}")
        
    def run_full_analysis(self):
        """Run complete APK analysis workflow"""
        try:
            # Step 1: Basic APK structure analysis
            self.analyze_apk_structure()
            
            # Step 2: Extract and analyze content
            self.extract_and_analyze()
            
            # Step 3: Try APKTool MCP decompilation
            self.try_apktool_mcp()
            
            # Step 4: Try Ghidra analysis
            self.try_ghidra_analysis()
            
            # Step 5: Security analysis
            self.security_analysis()
            
            # Step 6: Generate recommendations
            self.generate_recommendations()
            
            # Save final report
            self.save_report()
            
            return True
            
        except Exception as e:
            self.add_to_report(f"❌ Analysis failed: {e}")
            self.save_report()
            return False
    
    def analyze_apk_structure(self):
        """Analyze basic APK structure"""
        self.add_to_report("## 1. APK Structure Analysis")
        
        try:
            # Get file list from APK
            result = subprocess.run(["zipinfo", "-1", str(self.apk_path)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                
                # Categorize files
                dex_files = [f for f in files if f.endswith('.dex')]
                so_files = [f for f in files if f.endswith('.so')]
                xml_files = [f for f in files if f.endswith('.xml')]
                png_files = [f for f in files if f.endswith('.png')]
                jar_files = [f for f in files if f.endswith('.jar')]
                
                self.add_to_report(f"- **Total files:** {len(files)}")
                self.add_to_report(f"- **DEX files:** {len(dex_files)}")
                self.add_to_report(f"- **Native libraries:** {len(so_files)}")
                self.add_to_report(f"- **XML files:** {len(xml_files)}")
                self.add_to_report(f"- **Images:** {len(png_files)}")
                self.add_to_report(f"- **JAR files:** {len(jar_files)}")
                
                # Analyze native libraries
                if so_files:
                    architectures = set()
                    for so_file in so_files:
                        if '/' in so_file:
                            arch = so_file.split('/')[1] if so_file.startswith('lib/') else 'unknown'
                            architectures.add(arch)
                    
                    self.add_to_report(f"- **Supported architectures:** {', '.join(sorted(architectures))}")
                
                # Save detailed file list
                with open(self.output_dir / "file_list.txt", 'w') as f:
                    f.write('\n'.join(sorted(files)))
                
        except Exception as e:
            self.add_to_report(f"❌ Structure analysis failed: {e}")
        
        self.add_to_report("")
    
    def extract_and_analyze(self):
        """Extract APK and analyze contents"""
        self.add_to_report("## 2. Content Extraction and Analysis")
        
        try:
            extract_dir = self.output_dir / "extracted_apk"
            extract_dir.mkdir(exist_ok=True)
            
            # Extract APK
            result = subprocess.run([
                "unzip", "-q", str(self.apk_path), "-d", str(extract_dir)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.add_to_report("✅ APK extracted successfully")
                
                # Analyze AndroidManifest.xml (binary)
                manifest_path = extract_dir / "AndroidManifest.xml"
                if manifest_path.exists():
                    manifest_size = manifest_path.stat().st_size
                    self.add_to_report(f"- **AndroidManifest.xml:** {manifest_size:,} bytes (binary format)")
                
                # Analyze DEX files
                dex_files = list(extract_dir.glob("*.dex"))
                if dex_files:
                    self.add_to_report(f"- **DEX files found:** {len(dex_files)}")
                    total_dex_size = sum(dex.stat().st_size for dex in dex_files)
                    self.add_to_report(f"- **Total DEX size:** {total_dex_size:,} bytes")
                    
                    for dex in dex_files:
                        self.add_to_report(f"  - {dex.name}: {dex.stat().st_size:,} bytes")
                
                # Analyze native libraries
                lib_dir = extract_dir / "lib"
                if lib_dir.exists():
                    arch_dirs = [d for d in lib_dir.iterdir() if d.is_dir()]
                    self.add_to_report(f"- **Native library architectures:** {len(arch_dirs)}")
                    
                    for arch_dir in arch_dirs:
                        so_files = list(arch_dir.glob("*.so"))
                        total_size = sum(so.stat().st_size for so in so_files)
                        self.add_to_report(f"  - {arch_dir.name}: {len(so_files)} libraries ({total_size:,} bytes)")
                
                # Analyze resources
                res_dir = extract_dir / "res"
                if res_dir.exists():
                    layout_dir = res_dir / "layout"
                    drawable_dirs = [d for d in res_dir.iterdir() if d.name.startswith('drawable')]
                    
                    layout_count = len(list(layout_dir.glob("*.xml"))) if layout_dir.exists() else 0
                    drawable_count = sum(len(list(d.glob("*"))) for d in drawable_dirs)
                    
                    self.add_to_report(f"- **UI layouts:** {layout_count}")
                    self.add_to_report(f"- **Drawable resources:** {drawable_count}")
                
                # Analyze assets
                assets_dir = extract_dir / "assets"
                if assets_dir.exists():
                    asset_files = [f for f in assets_dir.rglob("*") if f.is_file()]
                    asset_size = sum(f.stat().st_size for f in asset_files)
                    self.add_to_report(f"- **Asset files:** {len(asset_files)} ({asset_size:,} bytes)")
            
            else:
                self.add_to_report(f"❌ APK extraction failed: {result.stderr}")
                
        except Exception as e:
            self.add_to_report(f"❌ Extraction failed: {e}")
        
        self.add_to_report("")
    
    def try_apktool_mcp(self):
        """Try to use APKTool MCP server for proper decompilation"""
        self.add_to_report("## 3. APKTool Decompilation Attempt")
        
        try:
            # Note: In a real environment with APKTool MCP server running,
            # you would use the MCP server functions here
            self.add_to_report("⚠️ APKTool MCP server integration pending")
            self.add_to_report("- Would decompile smali code from DEX files")
            self.add_to_report("- Would extract readable AndroidManifest.xml")
            self.add_to_report("- Would decode binary XML resources")
            
        except Exception as e:
            self.add_to_report(f"❌ APKTool MCP failed: {e}")
        
        self.add_to_report("")
    
    def try_ghidra_analysis(self):
        """Try to analyze with Ghidra"""
        self.add_to_report("## 4. Ghidra Binary Analysis")
        
        try:
            # Analyze DEX files with strings
            self.analyze_dex_strings()
            
            # Note: In a real environment, you would import into Ghidra and analyze
            self.add_to_report("⚠️ Full Ghidra analysis requires MCP server integration")
            self.add_to_report("- Would analyze DEX bytecode")
            self.add_to_report("- Would reverse engineer native libraries")
            self.add_to_report("- Would identify function calls and control flow")
            
        except Exception as e:
            self.add_to_report(f"❌ Ghidra analysis failed: {e}")
        
        self.add_to_report("")
    
    def analyze_dex_strings(self):
        """Analyze strings in DEX files for security indicators"""
        self.add_to_report("### String Analysis Results")
        
        try:
            # Extract DEX files
            temp_dir = Path("/tmp/dex_analysis_comprehensive")
            temp_dir.mkdir(exist_ok=True)
            
            subprocess.run(["unzip", "-q", str(self.apk_path), "*.dex", "-d", str(temp_dir)], 
                          capture_output=True)
            
            dex_files = list(temp_dir.glob("*.dex"))
            
            security_patterns = {
                'Network': ['http://', 'https://', 'ftp://', 'socket', 'tcp', 'udp'],
                'Crypto': ['encrypt', 'decrypt', 'cipher', 'crypto', 'hash', 'md5', 'sha'],
                'Authentication': ['password', 'secret', 'token', 'key', 'auth', 'login'],
                'Database': ['sql', 'sqlite', 'database', 'db', 'select', 'insert', 'update'],
                'System': ['root', 'admin', 'system', 'shell', 'exec', 'runtime'],
                'Debug': ['debug', 'log', 'trace', 'verbose', 'test'],
                'Privacy': ['location', 'gps', 'camera', 'microphone', 'contact', 'sms']
            }
            
            for dex_file in dex_files:
                result = subprocess.run(["strings", str(dex_file)], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    strings_content = result.stdout.lower()
                    
                    self.add_to_report(f"**{dex_file.name}:**")
                    
                    for category, patterns in security_patterns.items():
                        total_matches = sum(strings_content.count(pattern) for pattern in patterns)
                        if total_matches > 0:
                            self.add_to_report(f"- {category}: {total_matches} matches")
                            
                            # Show top patterns for this category
                            top_patterns = [(pattern, strings_content.count(pattern)) 
                                          for pattern in patterns 
                                          if strings_content.count(pattern) > 0]
                            top_patterns.sort(key=lambda x: x[1], reverse=True)
                            
                            for pattern, count in top_patterns[:3]:  # Top 3
                                self.add_to_report(f"  - {pattern}: {count}")
            
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            self.add_to_report(f"❌ String analysis failed: {e}")
    
    def security_analysis(self):
        """Perform security-focused analysis"""
        self.add_to_report("## 5. Security Analysis")
        
        try:
            # Check for common security indicators
            extract_dir = self.output_dir / "extracted_apk"
            
            security_findings = []
            
            # Check for debugging enabled
            if self.check_debug_enabled(extract_dir):
                security_findings.append("⚠️ Debug mode may be enabled")
            
            # Check for obvious security issues
            if self.check_network_security_config(extract_dir):
                security_findings.append("ℹ️ Network security configuration found")
            
            # Check for potential data storage
            if self.check_data_storage_indicators(extract_dir):
                security_findings.append("⚠️ Potential sensitive data storage detected")
            
            if security_findings:
                self.add_to_report("### Security Findings:")
                for finding in security_findings:
                    self.add_to_report(f"- {finding}")
            else:
                self.add_to_report("✅ No obvious security issues detected in basic analysis")
                
        except Exception as e:
            self.add_to_report(f"❌ Security analysis failed: {e}")
        
        self.add_to_report("")
    
    def check_debug_enabled(self, extract_dir):
        """Check if debug mode indicators are present"""
        # This would require parsing the binary AndroidManifest.xml
        # For now, check DEX files for debug strings
        try:
            dex_files = list(extract_dir.glob("*.dex"))
            for dex_file in dex_files:
                result = subprocess.run(["strings", str(dex_file)], 
                                      capture_output=True, text=True)
                if "debuggable" in result.stdout.lower():
                    return True
        except:
            pass
        return False
    
    def check_network_security_config(self, extract_dir):
        """Check for network security configuration"""
        return (extract_dir / "res" / "xml" / "network_security_config.xml").exists()
    
    def check_data_storage_indicators(self, extract_dir):
        """Check for potential sensitive data storage"""
        try:
            dex_files = list(extract_dir.glob("*.dex"))
            sensitive_patterns = ['password', 'private', 'secret', 'credential']
            
            for dex_file in dex_files:
                result = subprocess.run(["strings", str(dex_file)], 
                                      capture_output=True, text=True)
                content = result.stdout.lower()
                
                matches = sum(content.count(pattern) for pattern in sensitive_patterns)
                if matches > 10:  # Threshold for concern
                    return True
        except:
            pass
        return False
    
    def generate_recommendations(self):
        """Generate security recommendations"""
        self.add_to_report("## 6. Security Recommendations")
        
        recommendations = [
            "🔒 **Code Obfuscation**: Consider using code obfuscation to protect against reverse engineering",
            "🔐 **Certificate Pinning**: Implement certificate pinning for secure network communications", 
            "📱 **Root Detection**: Add root detection to prevent running on compromised devices",
            "🛡️ **Anti-Tampering**: Implement anti-tampering checks to detect code modifications",
            "🔍 **Regular Analysis**: Perform regular security analysis throughout development",
            "📝 **Secure Coding**: Follow secure coding practices for mobile applications",
            "🔄 **Update Dependencies**: Keep all dependencies and libraries up to date",
            "🧪 **Penetration Testing**: Consider professional penetration testing for production apps"
        ]
        
        for rec in recommendations:
            self.add_to_report(f"- {rec}")
        
        self.add_to_report("")
        self.add_to_report("---")
        self.add_to_report("*Analysis completed with APK Analysis Tool*")


if __name__ == "__main__":
    main()