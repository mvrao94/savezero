#!/usr/bin/env bash
# Instagram Saved Posts Cleanser - Linux / macOS Launcher

set -e
cd "$(dirname "$0")"

echo "========================================================"
echo "Starting Instagram Saved Posts Cleanser..."
echo "========================================================"

has_dependencies() {
    "$1" -c "import selenium, dotenv, webdriver_manager" &>/dev/null
}

# Prefer a project environment, then choose a dependency-ready interpreter.
if [ -x ".venv/bin/python" ] && has_dependencies ".venv/bin/python"; then
    PYTHON_CMD=".venv/bin/python"
elif command -v python3 &>/dev/null && has_dependencies "python3"; then
    PYTHON_CMD="python3"
elif command -v python3 &>/dev/null && python3 -m venv .venv &>/dev/null; then
    PYTHON_CMD=".venv/bin/python"
elif command -v python &>/dev/null && has_dependencies "python"; then
    PYTHON_CMD="python"
elif command -v python.exe &>/dev/null && has_dependencies "python.exe"; then
    PYTHON_CMD="python.exe"
else
    echo "Error: No usable Python environment was found."
    echo "Install Python 3.8+ and run this launcher again."
    exit 1
fi

if ! has_dependencies "$PYTHON_CMD"; then
    echo "Installing SaveZero dependencies..."
    "$PYTHON_CMD" -m pip install --disable-pip-version-check -e .
fi

exec "$PYTHON_CMD" cleaner.py "$@"
