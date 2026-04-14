#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Local macOS build script for Saltify
#
# Usage:
#   1. Activate your Python venv
#   2. Run:  bash scripts/macOS_exec.sh
#
# Prerequisites (install once via Homebrew):
#   brew install ffmpeg portaudio
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR="$SCRIPT_DIR/.."

# ---------------------------------------------------------------------------
# Download NLTK data if not already present
# ---------------------------------------------------------------------------
NLTK_DIR="$BASE_DIR/nltk_data"
if [ ! -d "$NLTK_DIR/tokenizers/punkt_tab" ]; then
  echo "⬇️  Downloading NLTK corpora into $NLTK_DIR …"
  python3 - <<'PYCODE'
import nltk, os
d = os.path.join(os.environ.get("BASE_DIR", "."), "nltk_data")
os.makedirs(d, exist_ok=True)
for c in ["wordnet","omw-1.4","punkt","punkt_tab",
          "averaged_perceptron_tagger","averaged_perceptron_tagger_eng",
          "wordnet_ic","stopwords"]:
    nltk.download(c, download_dir=d)
PYCODE
fi

# ---------------------------------------------------------------------------
# Resolve Homebrew paths for native libraries
# ---------------------------------------------------------------------------
FFMPEG_BIN="$(which ffmpeg)"
FFPROBE_BIN="$(which ffprobe)"
PA_LIB="$(find "$(brew --prefix portaudio)/lib" -name 'libportaudio*.dylib' | head -1)"

echo "📦  Bundling native deps:"
echo "  ffmpeg:    $FFMPEG_BIN"
echo "  ffprobe:   $FFPROBE_BIN"
echo "  portaudio: $PA_LIB"

# ---------------------------------------------------------------------------
# Build with PyInstaller
# ---------------------------------------------------------------------------
cd "$BASE_DIR"

pyinstaller --name Saltify \
  --windowed \
  --noconfirm \
  --onefile \
  --add-data "images:images" \
  --add-data "build_assets/en-model.slp:pattern/text/en" \
  --add-data "CTkXYFrame:CTkXYFrame" \
  --add-data "components:components" \
  --add-data "nltk_data:nltk_data" \
  --add-binary "$FFMPEG_BIN:." \
  --add-binary "$FFPROBE_BIN:." \
  --add-binary "$PA_LIB:." \
  --collect-data whisper \
  --collect-data lightning_fabric \
  --collect-data pytorch_lightning \
  --collect-data pyannote.audio \
  --collect-data sv_ttk \
  --collect-data language_tool_python \
  --copy-metadata torch \
  --copy-metadata tqdm \
  --copy-metadata regex \
  --copy-metadata sacremoses \
  --copy-metadata requests \
  --copy-metadata packaging \
  --copy-metadata filelock \
  --copy-metadata numpy \
  --copy-metadata tokenizers \
  --copy-metadata importlib_metadata \
  --hidden-import "lightning_fabric" \
  --hidden-import "torch" \
  --hidden-import "torchvision" \
  --hidden-import "pytorch_lightning" \
  --hidden-import "pyannote.audio" \
  --hidden-import "language_tool_python" \
  --hidden-import "PIL" \
  --hidden-import "PIL._tkinter_finder" \
  GUI.py

echo ""
echo "✅  Build complete!  Binary: dist/Saltify"
echo "    Run with:  ./dist/Saltify"