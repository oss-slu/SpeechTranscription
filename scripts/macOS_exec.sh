SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR="$SCRIPT_DIR/.."

VENV_NAME=$(basename "$VIRTUAL_ENV")

pyinstaller --onedir --windowed \
  --add-data "$BASE_DIR/images:images" \
  --add-data "$BASE_DIR/build_assets/en-model.slp:pattern/text/en" \
  --add-data "$BASE_DIR/CTkXYFrame:CTkXYFrame" \
  --add-binary "/usr/local/opt/portaudio/lib/libportaudio.2.dylib:." \
  --add-binary "/usr/local/bin/ffmpeg:." \
  --add-binary "/usr/local/bin/ffprobe:." \
  --collect-all lightning_fabric \
  --collect-all whisper \
  --collect-all pyannote.audio \
  --hidden-import torch \
  --hidden-import torchvision \
  "$BASE_DIR/GUI.py"q