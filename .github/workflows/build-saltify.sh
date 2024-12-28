#!/bin/bash

set -e

LOG_FILE="build.log"
exec > >(tee -i ${LOG_FILE}) 2>&1

# Step 1: Check and install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found, installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Step 2: Install MySQL and other dependencies
echo "Installing MySQL and other dependencies..."
brew install mysql pkg-config portaudio ffmpeg
brew services start mysql

# Step 3: Virtual Environment Setup (optional)
#echo "Setting up virtual environment..."
#python3 -m venv venv
#source venv/bin/activate

# Step 4: Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller importlib-metadata sacremoses tokenizers
pip uninstall -y typing

# Step 5: Install NLTK and resolve SSL issues
echo "Installing NLTK and resolving SSL issues..."
pip install nltk certifi
CERT_PATH=$(python -m certifi)
export SSL_CERT_FILE=${CERT_PATH}
export REQUESTS_CA_BUNDLE=${CERT_PATH}
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

# Step 6: Build the macOS executable with PyInstaller
echo "Building the macOS executable with PyInstaller..."
pyinstaller --name Saltify --windowed --noconfirm --onefile --debug all -c \
  --copy-metadata torch --copy-metadata tqdm --copy-metadata regex \
  --copy-metadata sacremoses --copy-metadata requests --copy-metadata packaging \
  --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers \
  --copy-metadata importlib_metadata --collect-data sv_ttk \
  --add-data "images:images" \
  --add-data "build_assets/en-model.slp:pattern/text/en" \
  --add-data "CTkXYFrame:CTkXYFrame" \
  --add-binary "$(brew --prefix portaudio)/lib/libportaudio.dylib:." \
  --add-binary "$(which ffmpeg):." \
  --add-binary "$(which ffprobe):." \
  GUI.py

# Step 7: Check for .txt file and rename if necessary
if [[ -f dist/Saltify.txt ]]; then
  echo "Found Saltify.txt instead of executable. Renaming..."
  mv dist/Saltify.txt dist/Saltify
fi

# Step 8: Move the executable
OUTPUT_DIR="dist/Saltify_$(date +'%Y%m%d_%H%M%S')"
mkdir -p "${OUTPUT_DIR}"
mv dist/Saltify "${OUTPUT_DIR}"

# Step 9: Ensure permissions are correct
chmod +x "${OUTPUT_DIR}/Saltify"

# Step 10: Clean up build files
echo "Cleaning up..."
rm -rf build *.spec

# Step 11: Notify user
osascript -e 'display notification "Build Complete!" with title "Saltify Build Script"'
echo "Build complete. The executable is located in ${OUTPUT_DIR}."
