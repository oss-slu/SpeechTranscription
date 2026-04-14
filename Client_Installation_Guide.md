# Client's Guide for Installing and Running SpeechTranscription

## System Requirements

The application is a self-contained executable — **no additional software** (Python, Java, etc.) needs to be installed.

> **Note:** Grammar checking uses an online API and requires an internet connection.

## Installation Instructions

1. Download the latest release ZIP for your operating system from the
   [GitHub Releases page](https://github.com/oss-slu/SpeechTranscription/releases):
   - `Saltify_macos.zip` for macOS
   - `Saltify_windows.zip` for Windows
2. Extract the ZIP file to a preferred location on your computer.
   - Right-click the downloaded file → **Extract All** → choose a folder.

## Running the Application

### Windows
- Open the extracted folder.
- Double-click **Saltify.exe**.

### macOS
- Open the extracted folder.
- Double-click **Saltify**.
- **First launch:** macOS Gatekeeper may block the app because it is not
  notarized. To allow it:
  1. Open **System Preferences → Privacy & Security**.
  2. Under *Security*, click **Open Anyway** next to the Saltify message.
  - Alternatively, run the following command in Terminal before first launch:
    ```
    xattr -cr /path/to/Saltify
    ```

## Notes for Clients

- You do **not** need to install Python, Java, or any other runtime —
  everything required is pre-packaged in the executable.
- Grammar checking requires an active internet connection (the feature
  uses the LanguageTool public API).
- All other features (transcription, playback, export) work fully offline.
- For Windows users: the first time the application is opened, you may be
  prompted to restart it. Close and reopen the application to continue.
- The application may take a moment to start on its first launch while
  it unpacks internal resources.
