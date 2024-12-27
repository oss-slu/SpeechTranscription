#!/bin/bash

# Exit immediately if any command fails
set -e

# Step 1: Check and install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found, installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Step 2: Install MySQL and other dependencies
echo "Installing MySQL and other dependencies..."
brew install mysql pkg-config portaudio ffmpeg  # Add ffmpeg if necessary
brew services start mysql
pip install pyaudio

# Step 3: Set MySQL environment variables (ensure they are available for your session)
echo "Setting MySQL environment variables..."
export MYSQLCLIENT_CFLAGS='pkg-config mysqlclient --cflags'
export MYSQLCLIENT_LDFLAGS='pkg-config mysqlclient --libs'

# Step 4: Install Python dependencies (ensure you're in the right virtualenv if required)
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt
pip install pyinstaller importlib-metadata sacremoses tokenizers

# Step 5: Install NLTK and handle SSL certificate issues
echo "Installing NLTK and resolving SSL certificate issues..."
pip install nltk certifi
CERT_PATH=$(python -m certifi)
export SSL_CERT_FILE=${CERT_PATH}
export REQUESTS_CA_BUNDLE=${CERT_PATH}
echo "Downloading NLTK resources..."
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# Step 6: Build executable using PyInstaller
echo "Building the macOS executable with PyInstaller..."
pyinstaller --name Saltify --windowed --noconfirm --onefile -c \
  --copy-metadata torch --copy-metadata tqdm --copy-metadata regex \
  --copy-metadata sacremoses --copy-metadata requests --copy-metadata packaging \
  --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers \
  --copy-metadata importlib_metadata --copy-metadata lightning_fabric \
  --collect-data sv_ttk --collect-data lightning_fabric --collect-data pytorch_lightning \
  --recursive-copy-metadata "openai-whisper" --collect-data whisper \
  --add-data "images:images" \
  --add-data "build_assets/en-model.slp:pattern/text/en" \
  --add-data "CTkXYFrame:CTkXYFrame" \
  --add-binary "$(brew --prefix portaudio)/lib/libportaudio.dylib:." \
  --add-binary "$(which ffmpeg):." \
  --add-binary "$(which ffprobe):." \
  GUI.py

# Step 7: Move the generated executable to the desired folder
echo "Moving the executable to the 'dist' directory..."
mkdir -p dist
mv dist/Saltify_macOS dist/Saltify

# Step 8: Notify user that the build is complete
echo "macOS build complete. The executable is located in 'dist/Saltify_macOS'."