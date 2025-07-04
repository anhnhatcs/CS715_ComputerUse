#!/bin/zsh

# Script to move log and screenshot files to their new locations
# This script should be run from the project root directory

# Source and destination directories
LOGS_SRC="cs715_coding/claude-computer-use-macos-add-streamlit-gui/logs"
LOGS_DEST="cs715_coding/data/logs"

SCREENSHOTS_SRC="cs715_coding/claude-computer-use-macos-add-streamlit-gui/screenshots"
SCREENSHOTS_DEST="cs715_coding/data/screenshots"

# Create destination directories if they don't exist
mkdir -p "$LOGS_DEST"
mkdir -p "$SCREENSHOTS_DEST"

# Copy log files
echo "Copying log files..."
cp -v "$LOGS_SRC"/*.json "$LOGS_DEST"/ 2>/dev/null || echo "No log files found."

# Copy screenshot files
echo "Copying screenshot files..."
cp -v "$SCREENSHOTS_SRC"/*.png "$SCREENSHOTS_DEST"/ 2>/dev/null || echo "No screenshot files found."

echo "Done."
