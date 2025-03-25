#!/bin/bash

set -e  # Exit script on any error
LOG_FILE="build.log"
exec > >(tee -i ${LOG_FILE}) 2>&1  # Log output to file and console

# Activate virtual environment
source "$(pwd)/venv/bin/activate"

echo "Virtual Environment Activated!"
echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Python version: $(python --version)"
echo "Installed packages:"
pip list

# Determine script and base directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR=$(git rev-parse --show-toplevel)
echo "Base directory: $BASE_DIR"
echo "Script directory: $SCRIPT_DIR"

# Detect virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Virtual environment not activated. Please activate it before running the script."
    exit 1
fi
VENV_NAME=$(basename "$VIRTUAL_ENV")

echo "Using virtual environment: $VENV_NAME"

# Step 1: Check and install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found, installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Step 2: Install dependencies
echo "Installing dependencies..."
brew install mysql pkg-config portaudio ffmpeg
brew services start mysql

# Step 3: Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r "$BASE_DIR/requirements.txt"
python -m pip install pyinstaller importlib-metadata sacremoses tokenizers
python -m pip uninstall -y typing

# Step 4: Install NLTK and resolve SSL issues
echo "Installing NLTK and fixing SSL issues..."
python -m pip install nltk certifi
CERT_PATH=$(python -m certifi)
export SSL_CERT_FILE=${CERT_PATH}
export REQUESTS_CA_BUNDLE=${CERT_PATH}
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

# Step 5: Check contents of dist/ before renaming
echo "Checking contents of dist/ before renaming:"
ls -la dist/

# Step 6: Build the macOS executable with PyInstaller
echo "Building the macOS executable..."
pyinstaller --onefile --windowed \
  --add-data "$(pwd)/images:images" \
  --add-data "$(pwd)/build_assets/en-model.slp:pattern/text/en" \
  --add-data "$(pwd)/CTkXYFrame:CTkXYFrame" \
  --add-binary "/opt/homebrew/opt/portaudio/lib/libportaudio.2.dylib:." \
  --add-binary "/opt/homebrew/bin/ffmpeg:." \
  --add-binary "/opt/homebrew/bin/ffprobe:." \
  --add-data "$VIRTUAL_ENV/lib/python3.11/site-packages/lightning_fabric:lightning_fabric" \
  --add-data "$VIRTUAL_ENV/lib/python3.11/site-packages/whisper:whisper" \
  --add-data "$VIRTUAL_ENV/lib/python3.11/site-packages/filelock:filelock" \
  --add-data "$VIRTUAL_ENV/lib/python3.11/site-packages/pytorch_lightning:torchlightning" \
  --add-data "$VIRTUAL_ENV/lib/python3.11/site-packages/pyannote:pyannote" \
  --hidden-import "lightning_fabric" \
  --hidden-import "torch" \
  --hidden-import "torchvision" \
  --hidden-import "pytorch_lightning" \
  --hidden-import "pyannote.audio" \
  "$(pwd)/GUI.py"

# Step 7: Fix potential PyInstaller .txt issue
if [[ -f dist/Saltify.txt ]]; then
  echo "Found Saltify.txt instead of executable. Renaming..."
  mv dist/Saltify.txt dist/Saltify
fi

# Step 8: Organize build output
OUTPUT_DIR="dist/Saltify_$(date +'%Y%m%d_%H%M%S')"
mkdir -p "${OUTPUT_DIR}"

# Check if the Saltify executable exists
if [ ! -f "dist/Saltify" ]; then
  echo "Error: dist/Saltify executable not found!"
  exit 1
fi

mv dist/Saltify "${OUTPUT_DIR}"

# Step 9: Ensure correct permissions
chmod +x "${OUTPUT_DIR}/Saltify"

# Step 10: Clean up temporary files
echo "Cleaning up..."
rm -rf build *.spec

# Step 11: Notify user
osascript -e 'display notification "Build Complete!" with title "Saltify Build Script"'
echo "Build complete. The executable is located in ${OUTPUT_DIR}."
