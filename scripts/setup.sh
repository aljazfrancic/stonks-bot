#!/bin/bash

# Stonks Bot Setup Script: creates .venv, installs dependencies and creates .env
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Setting up Stonks Bot..."

if command -v uv &> /dev/null; then
    echo "Creating virtual environment with uv..."
    uv venv --seed --allow-existing --python ">=3.12" .venv
    echo "Installing dependencies..."
    uv pip install --python .venv/bin/python -r requirements.txt
else
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Please install Python 3.12+ first." >&2
        exit 1
    fi

    # Check Python version
    if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 12))'; then
        echo "Python 3.12+ is required, found $(python3 --version)." >&2
        exit 1
    fi

    # On Debian/Ubuntu this needs the python3-venv package
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Installing dependencies..."
    .venv/bin/python -m pip install -r requirements.txt
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example. Please edit it with your actual API keys"
else
    echo ".env file already exists"
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate the virtual environment: source .venv/bin/activate"
echo "3. Run: python bot.py"
echo "4. Or show a chart locally: python stonks.py"
