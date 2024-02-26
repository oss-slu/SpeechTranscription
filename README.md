# SpeechTranscription

The primary purpose of the application is to transcribe an audio sample into a written format that is accepted by `SALT software`. SALT software is an app that analyzes the speech of children and scores it according to their metrics.
The app can currently transcribe audio samples of a conversation between a child and an adult into text. It will need to distinguish who is speaking though as well what is being said. Second, the app will need to transcribe errors and features that are auto-corrected in currently available speech-to-text programs. Children naturally produce speech sound errors, language errors, and language features such as disfluencies. Language errors and features are diagnostically meaningful to speech-language pathologists (SLPs) and need to be maintained in the transcription. Unlike any programs currently available, the app will also offer suggestions for coding the sample.

The program can currently be run by:
`python gui.py`

Requirements include:

* Allow the user to input participant/client information like name, age, gender and examiner details.
* Record and Transcribe an audio language sample into text that SLPs can transfer to SALT’s program.
* The transcription should automatically correct errors like accents and mispronounced letters. (e.g, bath instead of “baf”).
* The transcription should include errors like missed grammatical morphemes, missing words, incorrect word usage and ungrammatical sentences.
* Identify and label the speakers (For e.g., if a child says “I am fine” it should be represented as “C I am fine”).
* The user can play the audio and manually change the transcription.
* The program should be able to generate a transcription with SALT’s convention or without any conventions.
* Finally, there should be an option to export the transcription into a word document.


# Contributing as a Developer

## Development Environment
1. **Clone the Repository** - [This link](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) details how you can create a local clone of the repository. To do this, you need to have Git installed. Information for installing Git can be found [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
2. **Requirements** - This project uses Python, which can be downloaded [here](https://www.python.org/downloads/). Before attempting to run GUI.py with "python GUI.py" in your command line interface, you should install all the packages found in [requirements.txt](https://github.com/oss-slu/SpeechTranscription/blob/userGuides/requirements.txt). Look at the first line of requirements.txt to see instructions for how to install all of the packages at once.
    *   It may be beneficial to create a python virtual environment that contains only the packages required for this project. This allows you to isolate your development environment to be specialized for this project.
3. **Running the Program** - Simply type "python GUI.py" in the command line while in the repository to start the program.

## Using GitHub Issues when Adding Features and Fixing Bugs

- Use the [issues](https://github.com/oss-slu/SpeechTranscription/issues) page to keep track of changes that need to be made regarding features, documentation, and bugs. There is also a [board](https://github.com/orgs/oss-slu/projects/11) page which displays the issues in an easier to read manner.
- To contribute to the project, first either pick an issue or create a new issue, then create a new branch off of main that will be dedicated to that issue. For example, if I wanted to make a new branch, I would do "git checkout main", "git pull", "git branch (new branch name)", and "git checkout (new branch name)". Then, make changes you want to the code, commit them to the branch, and push them upstream. Once you believe your branch is ready to be merged to main, make a pull request.
   *  If you decide to add a dependency, add it to [requirements.txt](https://github.com/oss-slu/SpeechTranscription/blob/userGuides/requirements.txt) and to the [dependency spreadsheet](https://docs.google.com/spreadsheets/d/1rF7BZ1AXOtmjdwhdSJLrg7la8HMRzAXMdA9WOwaqiew/edit?usp=sharing) (if you don't have access to the spreadsheet, request for someone with authorization to add it.)
- Create a test if applicable in saltify_test.py to allow for quick testing of your code. This will be very helpful in the future if any code breaks.

## Creating an Executable

- Note: How to access executable:
   1. Click on the 'Actions' tab in GitHub
   2. On the left-hand side under 'Workflows', click on '.github/workflows/create-executable.yml'
   3. Find your desired version (check title and branch name to find th eone you want) and then click on it
   4. Scroll down to the 'Artifacts' section and download the MacOS or Windows version (depending on what OS you have)

1. **Install requirements** - To run pyinstaller a couple of installations are necessary. These can be done with:
   *  pip install pyinstaller
   *  pip install importlib-metadata
   *  pip install sacremoses

2. **Arguments and .spec Creation** - To create the windows exe, we ran this command while located in the directory with GUI.py:

   *  pyinstaller --noconfirm --onedir -c --copy-metadata torch --copy-metadata tqdm --copy-metadata regex --copy-metadata sacremoses --copy-metadata requests --copy-metadata packaging --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers --copy-metadata importlib_metadata --collect-data sv_ttk --recursive-copy-metadata "openai-whisper" --collect-data whisper GUI.py

   This uses pyinstaller to create a directory containing an executable for the software. We had to specify --onedir instead of --onefile which would have been much nicer but this command was not able to work for windows. We also were not able to hide the console popup as this would also crash the exe. Running this command will prompt the user to add a line to the GUI.spec due to a recursion limit error. Add "import sys" and "sys.setrecursionlimit(5000)" under the first line of the spec file then run ‘pyinstaller GUI.spec’ to create the exe and required files. After the executable is built, add ffmpeg.exe, ffprobe.exe, and ffplay to the distribution folder.

3. **Ease of Access** - There is also a gui version of pyinstaller which is very helpful. You can get this via:
   *  pip install auto-py-to-exe
   
## Python Version
   * Currently, our project is only able to be ran on specific versions of Python. 
   * Working Python versions: 3.10.x - 3.11.x
   * Before running 'python GUI.py', check that you are using one of the above listed Python versions by running 'python --version'.   

   # Getting started with SALTIFY

## **Downloading the Application**

[This link](https://github.com/oss-slu/SpeechTranscription/releases) will take you to a page where you can download the executable files. Please select the correct executable based on your operating system (Windows or macOS)

<br />
<br />

# Using the Application

## **Audio-Related Functionality**
### _The five buttons along the top row all contain audio-related functionality._
1. **Upload** - This button will allow you to choose a file from your file system to be uploaded as audio, which can later be transcribed to text using speech recognition via the **Transrcibe** button.
2. **Record** - This button will begin recording audio from your computer's default microphone. During recording, this button is replaced with a **Stop** button, which will end your recording.
3. **Play** - This button will play back the currently selected audio file, whether manually uploaded or recorded within the program. During playback, this button is replaced with a **Stop** button that allows you to stop playback.
    * Note that we currently recommend for the user to play back audio using their computer's default media player program, as we are still developing functions for pausing, scrubbing, and skipping, and rewinding audio. We eventually hope to have the program in a state where this isn't necessary!
4. **Download** - This button allows the user to download the currently uploaded audio to their file system. If you recorded a session within the application, this is what would allow you to download that audio as a .wav file.
5. **Transcribe** - This button converts the currently selected audio into text using speech recognition, which will be placed in the large box in the center of the application.
    * Note that the quality of recording and the quality of speaking will affect the results of this functionality. In some cases, it may be advisable to still manually transcribe the audio.

## **Providing Session Information**
### _The second row of buttons and the table along the left side allow the user to enter information about the session, including the participant name, age, gender, date of birth, date of sample, examiner name, and sampling context._

1. **Dropdown Button** - This button allows you to choose which piece of information you want to enter. If you make a mistake, don't worry, because you can simply resubmit the correct data.
2. **Entry Box** - This box is between the dropdown button and the submit button is a text box. Here, you can enter data for the relevant field.
3. **Submit** - This button allows you to submit the data entered for the selected field. This data will then appear in the left hand table.
4. **Session Information Table** - This table holds all information about the session that has been submitted. 
5. **Toggle Table** - This button allows the user to hide the table.

## **Editing the Raw Transcript**
### _The large box in the center of the application is used to handle the raw transcript before any conventions are applied to the text. If manually transcribing audio, please enter text in this box such that each sentence starts on a new line._

1. **Transcription Box** - This box should hold the text of the raw transcript.
2. **Unlock/Lock** - To avoid editing text accidentally, the user may lock the box at any time so that changes cannot be made to it. 
3. **Clear** - This button clears the transcription box. Be careful, as this action cannot be undone.
4. **Toggle Table** - This button allows the user to hide the transcription box.

## **Adding and Editing Conventions**
### _After the raw transcript is edited to liking, the user may move on to adding and editing conventions within the convention box._

1. **Grammar Check** - This button triggers what should be the first step of adding conventions, which is to add error coding. The application will look at each sentence from the raw transcript and check if it is grammatically correct. If so, it will be automatically added to the convention box, which is created upon pressing this button. If not, it will be added to a smaller rectangular box below the convention box, with an attempt at adding the correct error coding. The user can then edit this sentence to their liking and then the grammar checking process will continue with further sentences.
    * Note that not every grammatically incorrect sentence will be caught, and some attempts at corrections may not be perfect.
2. **Convention Box** - The large box to the right of the transcription box should hold text that will be edited to add conventions.
3. **Grammar Correction Box** - Below the convention box, this box will hold sentences that are caught as incorrect during the grammar check process. The user can edit the sentence in the box to correct the error coding.
    * Note that inflectional morphemes should not be added during this step.
4. **Submit** - This button appends the sentence within the grammar correction box to the convention box. Click this when you are finished editing a sentence within the grammar correction box.
5. **Add Morphemes** - After finishing the grammar check process (all sentences from the raw transcript should be in the convention box), the user may select this button to add inflectional morphemes to the text.
    * Note that not all inflectional morphemes will be added perfectly. We hope to resolve bugs of this type as quickly as possible.
6. **Lock/Unlock** and **Clear** - These buttons work similarly for the convention box as they did for the transcription box.

<br />
<br />

# Relaying Bugs to the Development Team

You may find that some features do not work as intended. Please either email the development team explaining your issue or go to [this link](https://github.com/oss-slu/SpeechTranscription/issues) where you can create a new "issue" and describe your problem. We are happy to help diagnose and resolve problems!