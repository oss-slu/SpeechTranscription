#!/bin/bash

set -x  # Exit script on any error
# Determine script and base directories FIRST
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR=$(git rev-parse --show-toplevel)

LOG_FILE="$BASE_DIR/build.log"
exec > >(tee -i ${LOG_FILE}) 2>&1  # Log output to file and console
echo "✅ build.log initialized at: $LOG_FILE"

echo "Base directory: $BASE_DIR"
echo "Script directory: $SCRIPT_DIR"

# Activate virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Virtual environment not activated. Please activate it before running the script."
    exit 1
fi
source "$VIRTUAL_ENV/bin/activate"
echo "Using virtual environment: $(basename "$VIRTUAL_ENV")"
PYTHON_SITE=$(python -c "import site; print(site.getsitepackages()[0])")

# Upgrade pip and install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$BASE_DIR/requirements.txt"

# Ensure Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found, installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Updating Homebrew..."
    brew update
fi

# Install required packages
for pkg in mysql pkg-config portaudio ffmpeg; do
    if ! brew list $pkg &>/dev/null; then
        brew install $pkg
    else
        echo "$pkg is already installed."
    fi
done
brew services start mysql

echo "Current working directory: $(pwd)"
echo "Pre-build directory contents:"
ls -la "$BASE_DIR"
# Install additional Python dependencies
pip install pyinstaller importlib-metadata sacremoses tokenizers

echo "Post-build dist contents:"
ls -la dist || echo "dist not created"

pip uninstall -y typing
pip install nltk certifi

# Fix SSL issues for NLTK
echo "Fixing SSL issues..."
CERT_PATH=$(python -m certifi)
export SSL_CERT_FILE=${CERT_PATH}
export REQUESTS_CA_BUNDLE=${CERT_PATH}
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

# Ensure required directories exist
mkdir -p dist release

# Build the macOS executable
echo "Building the macOS executable..."
pyinstaller --name=Saltify --onedir --windowed \
  --add-data "$BASE_DIR/images:images" \
  --add-data "$BASE_DIR/build_assets/en-model.slp:pattern/text/en" \
  --add-data "$BASE_DIR/CTkXYFrame:CTkXYFrame" \
  --add-binary "/opt/homebrew/opt/portaudio/lib/libportaudio.2.dylib:." \
  --add-binary "/opt/homebrew/bin/ffmpeg:." \
  --add-binary "/opt/homebrew/bin/ffprobe:." \
  --add-data "$PYTHON_SITE/lightning_fabric:lightning_fabric" \
  --add-data "$PYTHON_SITE/whisper:whisper" \
  --add-data "$PYTHON_SITE/filelock:filelock" \
  --add-data "$PYTHON_SITE/pytorch_lightning:torchlightning" \
  --add-data "$PYTHON_SITE/pyannote:pyannote" \
  --hidden-import "lightning_fabric" \
  --hidden-import "torch" \
  --hidden-import "torchvision" \
  --hidden-import "pytorch_lightning" \
  --hidden-import "pyannote.audio" \
  "$BASE_DIR/GUI.py"

# Check build output
if [ ! -d "dist/Saltify" ]; then
    echo "Error: dist/Saltify executable not found!"
    ls -la dist/
    exit 1
fi

# Organize build output into release directory
RELEASE_DIR="release/Saltify_$(date +'%Y%m%d_%H%M%S')"
mkdir -p "${RELEASE_DIR}"
mv dist/Saltify "${RELEASE_DIR}"
chmod +x "${RELEASE_DIR}/Saltify/Saltify"

# Clean up temporary files
rm -rf build *.spec dist/

echo "Build complete. The executable is located in ${RELEASE_DIR}."

# Notify user (only if not running in CI/CD)
if [[ -z "$CI" || -z "$GITHUB_ACTIONS" ]]; then
    osascript -e 'display notification "Build Complete!" with title "Saltify Build Script"'
fi

echo "Full PyInstaller log:"
tail -n 20 "$LOG_FILE"
