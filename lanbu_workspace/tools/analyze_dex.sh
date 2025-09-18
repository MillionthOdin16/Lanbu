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
