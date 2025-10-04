#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Verify google-generativeai is installed
if ! python -c "import google.generativeai" &> /dev/null; then
    echo "Error: google-generativeai is not installed correctly!"
    pip install --force-reinstall google-generativeai
fi

echo "Build completed successfully"
