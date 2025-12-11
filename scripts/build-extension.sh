#!/bin/bash
set -e

echo "Building Firefox extension..."

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to extension directory and create zip
cd "$PROJECT_ROOT/extension"
zip -r ../aw-bookmark-extension.zip .

echo "✓ Created aw-bookmark-extension.zip"
echo ""
echo "Ready to upload to https://addons.mozilla.org/developers/"
echo ""
echo "To verify the zip structure:"
echo "  unzip -l aw-bookmark-extension.zip | head -20"
