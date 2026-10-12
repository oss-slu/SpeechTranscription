# Client's Guide for Installing and Running SpeechTranscription

# System Requirements

* Windows 10/11 (64-bit), or macOS on Apple Silicon (M1 or newer).
* You do not need to install Java or Python, or change any environment variables. Both releases include them.
* ffmpeg (used for audio):
    * macOS: included in the release.
    * Windows: installed automatically the first time you open the app (see Running the Application).
* An internet connection for the first-time setup steps listed under Notes. After that, the app works offline.

# Installation Instructions

* Download the latest release zip for your operating system from the [GitHub Releases page](https://github.com/oss-slu/SpeechTranscription/releases):
    * `Saltify_macos.zip` for macOS
    * `Saltify_windows.zip` for Windows
* Extract the zip file to a folder of your choice.
    * Windows: right-click the downloaded file, choose Extract All, then choose a folder.
    * macOS: double-click the downloaded zip.

# Running the Application

## Windows

1. Open the extracted folder and double-click `Saltify.exe`.
2. The first time, the app installs ffmpeg using Windows Package Manager (winget). Accept any prompts that appear.
3. When the app shows "Restart Required", close it and open it again. Transcription works after this restart. This only happens once.

## macOS

1. Open the extracted folder and double-click `Saltify`.
2. The first time, macOS may say it cannot verify that "Saltify" is free of malware. Right-click (or Control-click) `Saltify`, choose Open, then click Open again.
3. If that option does not appear, open Terminal in the extracted folder and run:

   ```
   xattr -dr com.apple.quarantine ./Saltify && chmod +x ./Saltify && ./Saltify
   ```

# Notes

* The app can take up to a minute to open, because it unpacks itself each time it starts.
* One-time downloads that need an internet connection:
    * The first transcription downloads the speech recognition model (about 460 MB).
    * The first Grammar Check downloads the grammar checking engine (about 250 MB).
    * Windows only: the ffmpeg install on first launch.
