pyinstaller --onefile --noconsole \
    --add-data="/Users/ksp/Desktop/temp/SpeechTranscription/images:images" \
    --add-data="/Users/ksp/Desktop/temp/SpeechTranscription/build_assets/en-model.slp:build_assets" \
    --add-data="CTkXYFrame:CTkXYFrame" \
    --add-binary="/opt/homebrew/opt/portaudio/lib/libportaudio.2.dylib:." \
    --add-binary="/opt/homebrew/bin/ffmpeg:." \
    --add-binary="/opt/homebrew/bin/ffprobe:." \
    --add-data="/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages:site-packages" \
    --add-data="/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/whisper:whisper" \
    --add-data="/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/filelock:filelock" \
    --add-data="/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/typing_extensions:typing_extensions" \
    --add-data="/Users/ksp/Desktop/temp/SpeechTranscription/myenv/lib/python3.11/site-packages/lightning_fabric/version.info:lightning_fabric" \
    --hidden-import="lightning_fabric" \
    --hidden-import="lightning_fabric.version" \
    --hidden-import="torch" \
    --hidden-import="torchvision" \
    --hidden-import="typing_extensions" \
    --collect-all lightning_fabric \
    GUI.py