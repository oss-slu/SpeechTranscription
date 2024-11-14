#!/bin/bash

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt pyinstaller customtkinter

# Build the executable with PyInstaller
pyinstaller --name Saltify --windowed --noconfirm --onefile \
  --add-data "application/static:static" \
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

# Deactivate the virtual environment
deactivate

# Set permissions for macOS
chmod +x dist/Saltify

echo "Build complete. Check the dist/ directory."
