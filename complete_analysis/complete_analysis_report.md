# Complete APK Analysis Report

**APK**: lanbu.apk
**Size**: 34,055,115 bytes
**Analysis Date**: Thu Sep 18 15:55:35 UTC 2025

## File Structure Summary

| File Type | Count |
|-----------|-------|
| .png | 208 |
| .xml | 202 |
| .version | 44 |
| .properties | 31 |
| .kotlin_builtins | 7 |
| .so | 7 |
| .dat | 4 |
| .dex | 3 |
| .json | 3 |
| No extension | 3 |

**Total files**: 526

## Key Findings

- **Application Type**: Unity-based mobile game
- **Development Status**: Debug build (uses debug certificate)
- **Analytics**: Extensive Firebase integration
- **Monetization**: Google AdMob integration
- **Platform**: Android ARM64 native libraries
- **Framework**: Modern AndroidX libraries

## Recommendations

1. **Security**: App uses debug certificate - not suitable for production
2. **Privacy**: Extensive tracking and analytics capabilities
3. **Performance**: Large DEX files suggest unoptimized build
4. **Further Analysis**: Use APKTool for full decompilation of resources
