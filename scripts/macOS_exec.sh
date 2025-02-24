pyinstaller --onefile --noconsole \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/images:images" \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/build_assets/en-model.slp:pattern/text/en" \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/CTkXYFrame:CTkXYFrame" \
  --add-binary "/opt/homebrew/opt/portaudio/lib/libportaudio.2.dylib:." \
  --add-binary "/opt/homebrew/bin/ffmpeg:." \
  --add-binary "/opt/homebrew/bin/ffprobe:." \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/lightning_fabric:lightning_fabric" \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/whisper:whisper" \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/filelock:filelock" \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/lightning_fabric/version.info:lightning_fabric" \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/pytorch_lightning:torchlightning" \
  --add-data "/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/pyannote:pyannote" \
  --hidden-import "lightning_fabric" \
  --hidden-import "torch" \
  --hidden-import "torchvision" \
  --hidden-import "pytorch_lightning" \
  --hidden-import "pyannote.audio" \
  /Users/ksp/Desktop/temp/SpeechTranscription/GUI.py
  