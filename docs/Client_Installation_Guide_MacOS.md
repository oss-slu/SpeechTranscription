# Client's Guide for Installing and Running SpeechTranscription
# System Requirements

Before installing, ensure your system meets these requirements:
* Operating System: macOS, Windows, or Linux
* Python: Version 3.11.x
* Java: Installed on your system [Download Here](https://www.oracle.com/java/technologies/downloads/)
* MySQL: Installed and running [Download Here](https://dev.mysql.com/downloads/mysql/)

# Installation Instructions
* Download the latest release zip for your operating system from the GitHub Releases page:
    * saltify_macos.zip for macOS
    * saltify_windows.zip for Windows
* Extract the zip file to a preferred location on your computer.

# Setup for macOS
* Open Terminal and navigate to the extracted folder: 
    * cd /path/to/SpeechTranscription
* Create and activate the Python virtual environment: 
    * python3 -m venv venv
    * source venv/bin/activate
* Install dependencies: 
    * pip install -r requirements.txt
* For Mac users, the following libraries may need extra setup:
    * brew install portaudio ffmpeg mysql pkg-config
    * pip install pyaudio
    * pip install mysql-connector-python
* Run the program:
    * python GUI.py


