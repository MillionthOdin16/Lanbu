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
