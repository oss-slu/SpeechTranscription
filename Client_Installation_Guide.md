# Client's Guide for Installing and Running SpeechTranscription
# System Requirements

* No Java, Python, or ffmpeg installation is needed. Everything required is packaged with the release.
* macOS release: Apple Silicon (M1 or newer).
* An internet connection is needed the first time you transcribe and the first time you run Grammar Check (see Notes).

# Installation Instructions
* Download the latest release zip for your operating system from the GitHub Releases page (https://github.com/oss-slu/SpeechTranscription/releases):
    * Saltify_macos.zip for macOS
    * Saltify_windows.zip for Windows
* Extract the zip file to a preferred location on your computer.
    * Windows: right-click the downloaded file, choose Extract All, then choose a folder.
    * macOS: double-click the downloaded zip.

# Running the Application
* Windows: open the extracted folder and double-click `Saltify.exe`.
* macOS: open the extracted folder and double-click `Saltify`.
    * The first time, macOS may say it cannot verify that "Saltify" is free of malware. Right-click (or Control-click) `Saltify`, choose Open, then click Open again.
    * If that option does not appear, open Terminal in the extracted folder and run:
      `xattr -dr com.apple.quarantine ./Saltify && chmod +x ./Saltify && ./Saltify`

# Notes for Clients
* You do not need to modify environment variables—everything required for running the app is pre-packaged.
* The app takes some time to open.
* The first transcription downloads the speech recognition model (about 460 MB), and the first Grammar Check downloads the grammar checking engine (about 250 MB). Both are one-time downloads; after that these features work offline.
* For Windows users: The first time the application is opened, you may be prompted to restart it. Close and reopen the application to use.
