#!/bin/bash

# Determine the OS (macOS or Linux)
OS=$(uname -s)
if [[ "$OS" == "Darwin" ]]; then
    echo "Building on macOS..."
elif [[ "$OS" == "Linux" ]]; then
    echo "Building on Linux..."
else
    echo "Unsupported operating system: $OS"
    exit 1
fi

# Step 1: Create a virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 2: Upgrade pip and install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt pyinstaller customtkinter

# Step 3: Download NLTK corpora
echo "Downloading NLTK corpora..."
python -m nltk.downloader all

# Step 4: Ensure Java is installed and accessible
if command -v java &> /dev/null; then
    echo "Java is installed:"
    java -version
else
    echo "Java is not installed. Please install it and try again."
    deactivate
    exit 1
fi

# Step 5: Build the executable with PyInstaller
echo "Building the Saltify executable..."
pyinstaller --name Saltify --windowed --noconfirm --onefile \
  --copy-metadata torch \
  --copy-metadata tqdm \
  --copy-metadata regex \
  --copy-metadata sacremoses \
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

# Step 6: Clean up and set permissions for macOS
echo "Setting permissions for the executable..."
chmod +x dist/Saltify

# Step 7: Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Build completed. Check the dist/ directory for the output."
