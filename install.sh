#!/usr/bin/env bash
# macOS / Linux One-Line Installer for agy-memory-pkm
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="python3"

if ! command -v "$PYTHON_CMD" &>/dev/null; then
    PYTHON_CMD="python"
fi

"$PYTHON_CMD" "$SCRIPT_DIR/install.py" "$@"
