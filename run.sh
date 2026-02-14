#!/bin/bash
# LaTeX to Mind Map Converter - Easy Run Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="$SCRIPT_DIR/.venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Virtual environment not found. Please run:"
    echo "python -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Run the script with the virtual environment Python
"$PYTHON_PATH" "$SCRIPT_DIR/latex_to_mindmap.py" "$@"