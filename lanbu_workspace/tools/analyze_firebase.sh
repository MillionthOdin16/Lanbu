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
