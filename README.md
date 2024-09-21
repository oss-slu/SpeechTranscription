# SpeechTranscription

The primary purpose of the application is to transcribe an audio sample into a written format that is accepted by `SALT software`. SALT software is an app that analyzes the speech of children and scores it according to their metrics.
The app can currently transcribe audio samples of a conversation between a child and an adult into text. It will need to distinguish who is speaking though as well what is being said. Second, the app will need to transcribe errors and features that are auto-corrected in currently available speech-to-text programs. Children naturally produce speech sound errors, language errors, and language features such as disfluencies. Language errors and features are diagnostically meaningful to speech-language pathologists (SLPs) and need to be maintained in the transcription. Unlike any programs currently available, the app will also offer suggestions for coding the sample.

The program can currently be run by:
`python gui.py`

   # Getting started with SALTIFY

## **Downloading the Application**

[This link](https://github.com/oss-slu/SpeechTranscription/releases) will take you to a page where you can download the executable files. Please select the correct executable based on your operating system (Windows or macOS)

In this application, you can record live or upload an audio file form your computer, and then transcribe it to a text output and then receuve suggested fixes for incorrect speech from our application. After this, you can download the output results to a docx format to save on your device and/or print.

# Contributing as a Developer

## Development Environment

For details on setting up the development environment, please refer to the [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) file.

## Creating an Executable

- Note: An executable is automatically generated using GitHub Actions.

- How to access executable for Windows:
   1. Click on the 'Actions' tab in GitHub
   2. On the left-hand side under 'Workflows', click on '.github/workflows/create-executable.yml'
   3. Find your desired version (check title and branch name to find th eone you want) and then click on it
   4. Scroll down to the 'Artifacts' section and download Windows version.

- How to access executable for MacOS:
   1. Follow this tutorial until 4:10 in the video: https://youtu.be/5Z_G6QG7xxg?si=zg5MozBv6WrYJtIQ 
   2. Once in the Windows virtual machine, follow the above instructions (steps 1-4) and then you will be able to run the executable on MacOS
 
 - Note: You can also manually create an executable using pyinstaller (see GitHub Actions for commands to run to achieve this). 
    
<br />
<br />

# Relaying Bugs to the Development Team

You may find that some features do not work as intended. Please either email the development team explaining your issue or go to [this link](https://github.com/oss-slu/SpeechTranscription/issues) where you can create a new "issue" and describe your problem. We are happy to help diagnose and resolve problems!