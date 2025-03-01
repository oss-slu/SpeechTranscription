#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

BASE_DIR="$SCRIPT_DIR/.."

pyinstaller --onefile --noconsole \
  --add-data "$BASE_DIR/images:images" \
  --add-data "$BASE_DIR/build_assets/en-model.slp:pattern/text/en" \
  --add-data "$BASE_DIR/CTkXYFrame:CTkXYFrame" \
  --add-binary "/opt/homebrew/opt/portaudio/lib/libportaudio.2.dylib:." \
  --add-binary "/opt/homebrew/bin/ffmpeg:." \
  --add-binary "/opt/homebrew/bin/ffprobe:." \
  --add-data "$BASE_DIR/myenv/lib/python3.11/site-packages/lightning_fabric:lightning_fabric" \
  --add-data "$BASE_DIR/myenv/lib/python3.11/site-packages/whisper:whisper" \
  --add-data "$BASE_DIR/myenv/lib/python3.11/site-packages/filelock:filelock" \
  --add-data "$BASE_DIR/myenv/lib/python3.11/site-packages/lightning_fabric/version.info:lightning_fabric" \
  --add-data "$BASE_DIR/myenv/lib/python3.11/site-packages/pytorch_lightning:torchlightning" \
  --add-data "$BASE_DIR/myenv/lib/python3.11/site-packages/pyannote:pyannote" \
  --hidden-import "lightning_fabric" \
  --hidden-import "torch" \
  --hidden-import "torchvision" \
  --hidden-import "pytorch_lightning" \
  --hidden-import "pyannote.audio" \
  "$BASE_DIR/GUI.py"