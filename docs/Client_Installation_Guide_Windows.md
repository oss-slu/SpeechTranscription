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

# Setup for Windows/Linux
* Open a Command Prompt (Windows) or Terminal (Linux) and navigate to the extracted folder:
    * cd \path\to\SpeechTranscription
* Install Python dependencies:
    * pip install -r requirements.txt
* Download the NLTK data:
    * pip install nltk
    * python -m nltk.downloader all
* Run the program :
    * python GUI.py

# Running the Application
* Double-check that the virtual environment is activated (macOS users).
* Launch the application using:
    * python GUI.py
* The GUI should appear, and you can begin using the SpeechTranscription features immediately.

# Notes for Clients
* You do not need to modify environment variables—everything required for running the app is pre-packaged.
* If you face issues with MySQL connection, make sure the MySQL server is running and accessible.
* The application does not require Python installation if packaged with the executable (for releases).

