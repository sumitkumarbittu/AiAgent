#!/usr/bin/env bash
# Exit on error
set -o errexit

# Ensure we're using Python 3.9
if ! command -v python3.9 &> /dev/null; then
    echo "Python 3.9 is required but not found. Please install it first."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3.9 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and setuptools
python -m pip install --upgrade pip==21.3.1
pip install setuptools==67.8.0 wheel==0.40.0

# Install build dependencies first
pip install cython==0.29.33

# Install Python dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Verify critical packages are installed
for pkg in "google.generativeai" "flask" "gunicorn"; do
    if ! python -c "import ${pkg}" &> /dev/null; then
        echo "Error: ${pkg} is not installed correctly!"
        exit 1
    fi
done

echo "Build completed successfully"
