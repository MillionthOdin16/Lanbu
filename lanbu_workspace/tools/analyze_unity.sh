#!/bin/bash
# Analyze Unity-specific components

echo "🎮 Analyzing Unity components..."

cd "../extracted"

echo "📋 Unity configuration:"
echo "--- boot.config ---"
cat assets/bin/Data/boot.config 2>/dev/null || echo "File not found"
echo

echo "📋 Unity app GUID:"
cat assets/bin/Data/unity_app_guid 2>/dev/null || echo "File not found"
echo

echo "📋 Runtime initialization:"
cat assets/bin/Data/RuntimeInitializeOnLoads.json 2>/dev/null | jq . || echo "File not found or invalid JSON"
echo

echo "📋 Scripting assemblies:"
cat assets/bin/Data/ScriptingAssemblies.json 2>/dev/null | jq . || echo "File not found or invalid JSON"
echo

echo "📊 Asset sizes:"
ls -lh assets/bin/Data/ | grep -E "\.(unity3d|dat|json)$"
