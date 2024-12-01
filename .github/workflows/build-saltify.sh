#!/bin/bash

# Ensure the script runs only on macOS
OS=$(uname -s)
if [[ "$OS" != "Darwin" ]]; then
    echo "This script is designed to run only on macOS."
    exit 1
fi

# Step 1: Initialize and update submodules
echo "Initializing and updating Git submodules..."
git submodule init
git submodule update

# Step 2: Create a virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 3: Upgrade pip and install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt pyinstaller customtkinter

# Ensure 'typing' is not installed
if pip show typing &> /dev/null; then
    echo "Removing obsolete 'typing' package..."
    pip uninstall -y typing
fi

# Step 4: Download NLTK corpora
echo "Downloading NLTK corpora..."
python -m nltk.downloader all

# Step 5: Ensure Java is installed and accessible
if command -v java &> /dev/null; then
    echo "Java is installed:"
    java -version
else
    echo "Java is not installed. Please install it and try again."
    deactivate
    exit 1
fi

# Step 6: Build the executable with PyInstaller
echo "Building the Saltify macOS executable..."
pyinstaller --name Saltify --windowed --noconfirm --onefile \
  --copy-metadata torch \
  --copy-metadata tqdm \
  --copy-metadata regex \
  --copy-metadata sacremoses \
  --copy-metadata tokenizers \
  --copy-metadata requests \
  --copy-metadata packaging \
  --copy-metadata filelock \
  --copy-metadata numpy \
  --copy-metadata tokenizers \
  --copy-metadata customtkinter \
  --copy-metadata importlib_metadata \
  --collect-data sv_ttk \
  --collect-data customtkinter \
  --recursive-copy-metadata "openai-whisper" \
  --collect-data whisper \
  GUI.py

# Step 7: Zip the output
echo "Zipping the macOS output..."
zip -r dist/Saltify.zip dist/Saltify

# Step 8: Clean up and deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Build completed. Check the dist/ directory for the macOS executable."
