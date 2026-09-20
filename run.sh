#!/usr/bin/env bash
# Instagram Saved Posts Cleanser - Linux / macOS Launcher

set -e
cd "$(dirname "$0")"

echo "========================================================"
echo "Starting Instagram Saved Posts Cleanser..."
echo "========================================================"

# Check if python3 is available
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python is not installed or not in PATH."
    exit 1
fi

$PYTHON_CMD cleaner.py "$@"
