#!/bin/bash

set -x  # Exit script on any error
# Determine script and base directories FIRST
SCRIPT_DIR="$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" &> /dev/null && pwd )"
BASE_DIR=$(git rev-parse --show-toplevel)

LOG_FILE="$BASE_DIR/build.log"
exec > >(tee -i ${LOG_FILE}) 2>&1  # Log output to file and console
echo "✅ build.log initialized at: $LOG_FILE"

echo "Base directory: $BASE_DIR"
echo "Script directory: $SCRIPT_DIR"

# Ensure virtualenv is active, else activate it
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Virtual environment not activated. Attempting to activate..."
    if [ -f "$BASE_DIR/venv/bin/activate" ]; then
        source "$BASE_DIR/venv/bin/activate"
    else
        echo "❌ No virtual environment found at $BASE_DIR/venv"
        exit 1
    fi
fi

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

# Clean up incompatible packages and ensure fat binaries
echo "📦 Removing non-fat packages that break universal2 build..."
pip uninstall -y typing || true
pip uninstall -y PyYAML || true

# Reinstall only universal2-compatible PyYAML (via Conda or avoid if unnecessary)
echo "📦 Installing dependencies (skip PyYAML if not explicitly needed)"
pip install pyinstaller importlib-metadata sacremoses tokenizers
pip install nltk certifi

# Fix SSL issues for NLTK
CERT_PATH=$(python -m certifi)
export SSL_CERT_FILE=${CERT_PATH}
export REQUESTS_CA_BUNDLE=${CERT_PATH}
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

# Ensure required directories exist
mkdir -p dist release

# Build the macOS executable
echo "Building the macOS executable..."
pyinstaller --log-level=DEBUG --name=Saltify \
  --windowed \
  --noconfirm \
  --osx-bundle-identifier=com.saltify.transcriber \
  --clean \
  --onedir \
  --distpath dist \
  --workpath build \
  --specpath build \
  --add-data "$BASE_DIR/images:images" \
  --add-data "$BASE_DIR/build_assets/en-model.slp:pattern/text/en" \
  --add-data "$BASE_DIR/CTkXYFrame:CTkXYFrame" \
  --add-binary "${PORTAUDIO_PATH:-/usr/lib/libportaudio.so}:." \
  --add-binary "${FFMPEG_PATH:-/usr/bin/ffmpeg}:." \
  --add-binary "${FFPROBE_PATH:-/usr/bin/ffprobe}:." \
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

# If PyInstaller fails, exit immediately with log info
if [ $? -ne 0 ]; then
  echo "❌ PyInstaller failed. Dumping last 40 lines of log:"
  tail -n 40 "$LOG_FILE"
  exit 1
fi

# List build outputs
echo "✅ PyInstaller build directory contents:"
ls -la dist || echo "dist does not exist"
ls -la build || echo "build does not exist"

# Mark .app binary executable if it exists
chmod +x dist/Saltify.app/Contents/MacOS/Saltify || echo "❌ Could not chmod binary inside .app"

# Notify user (only if not running in CI/CD)
if [[ -z "$CI" || -z "$GITHUB_ACTIONS" ]]; then
    osascript -e 'display notification "Build Complete!" with title "Saltify Build Script"'
fi

echo "Full PyInstaller log:"
tail -n 20 "$LOG_FILE"
