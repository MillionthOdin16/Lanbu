# APK Analysis with Docker

This document explains how to use the APK analysis tools with Docker for maximum compatibility and ease of deployment.

## Quick Start

### Option 1: Volume Mounting (Recommended)

Place your APK files in a directory and mount it to the container:

```bash
# Build the container
docker build -t lanbu .

# Analyze APK files in /path/to/your/apks directory
docker run --rm -v /path/to/your/apks:/workspace lanbu docker-apk-analysis

# Example with a specific APK
mkdir my_apks
cp my-app.apk my_apks/
docker run --rm -v $(pwd)/my_apks:/workspace lanbu docker-apk-analysis
```

### Option 2: Copy APK into Container

For one-time analysis, you can modify the Dockerfile to include your APK:

```dockerfile
# Add this line to Dockerfile before the final WORKDIR
COPY your-app.apk /workspace/
```

Then build and run:
```bash
docker build -t lanbu-with-apk .
docker run --rm lanbu-with-apk docker-apk-analysis
```

## Analysis Outputs

All analysis results are saved to `/workspace/analysis_results/` inside the container. When using volume mounting, these files will be available on your host system.

Generated files include:
- `SUMMARY.md` - Overall analysis summary
- `security_report.md` - Security-focused findings
- `dex_analysis.json` - DEX file analysis results
- `file_listing.txt` - Complete APK file inventory
- `extracted/` - Extracted APK contents

## MCP Server Integration

The MCP servers are designed to work with volume-mounted workspaces:

```json
{
  "mcpServers": {
    "apk_analysis": {
      "type": "local",
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/workspace:/workspace", "-w", "/workspace", "lanbu", "docker-apk-analysis"],
      "tools": ["*"]
    }
  }
}
```

## Troubleshooting

### APK Not Found
- Ensure your APK is in the mounted directory
- Check volume mount paths: `-v /host/path:/workspace`
- Verify APK file permissions are readable

### Analysis Fails
- Ensure container has sufficient disk space
- Check that required tools (unzip, strings, etc.) are available
- Review container logs for specific errors

### Permission Issues
- Make sure the user running Docker has access to the APK files
- Consider using `--user $(id -u):$(id -g)` flag for proper permissions

## Advanced Usage

### Custom Workspace Location
```bash
# Use custom workspace directory
docker run --rm -v /my/custom/path:/workspace -e APK_ANALYSIS_WORKSPACE=/workspace lanbu docker-apk-analysis
```

### Multiple APK Analysis
```bash
# Analyze all APKs in a directory
for apk in /path/to/apks/*.apk; do
    docker run --rm -v "$(dirname $apk):/workspace" lanbu docker-apk-analysis /workspace/$(basename $apk)
done
```

### Integration with CI/CD
```yaml
# Example GitHub Actions step
- name: Analyze APK
  run: |
    docker build -t lanbu .
    docker run --rm -v ${{ github.workspace }}:/workspace lanbu docker-apk-analysis
```