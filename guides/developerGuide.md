# Contributing as a Developer

## Development Environment
1. **Clone the Repository** - [This link](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) details how you can create a local clone of the repository. To do this, you need to have Git installed. Information for installing Git can be found [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
2. **Requirements** - This project uses Python, which can be downloaded [here](https://www.python.org/downloads/). Before attempting to run GUI.py with "python GUI.py" in your command line interface, you should install all the packages found in [requirements.txt](https://github.com/oss-slu/SpeechTranscription/blob/userGuides/requirements.txt). For example, typing "pip install git+https://github.com/openai/whisper.git" will install the whisper package, which we use for speech recognition.
    *   It may be beneficial to create a python virtual environment that contains only the packages required for this project. This allows you to isolate your development environment to be specialized for this project.
3. **Running the Program** - Simply type "python GUI.py" in the command line while in the repository to start the program.

## Using GitHub Issues when Adding Features and Fixing Bugs

- Use the [issues](https://github.com/oss-slu/SpeechTranscription/issues) page to keep track of changes that need to be made regarding features, documentation, and bugs. There is also a [board](https://github.com/orgs/oss-slu/projects/11) page which displays the issues in an easier to read manner.
- To contribute to the project, first either pick an issue or create a new issue, then create a new branch off of main that will be dedicated to that issue. For example, if I wanted to make a new branch, I would do "git checkout main", "git pull", "git branch (new branch name)", and "git checkout (new branch name)". Then, make changes you want to the code, commit them to the branch, and push them upstream. Once you believe your branch is ready to be merged to main, make a pull request.
   *  If you decide to add a dependency, add it to [requirements.txt](https://github.com/oss-slu/SpeechTranscription/blob/userGuides/requirements.txt) and to the [dependency spreadsheet](https://docs.google.com/spreadsheets/d/1rF7BZ1AXOtmjdwhdSJLrg7la8HMRzAXMdA9WOwaqiew/edit?usp=sharing) (if you don't have access to the spreadsheet, request for someone with authorization to add it.)
- Create a test if applicable in saltify_test.py to allow for quick testing of your code. This will be very helpful in the future if any code breaks.

## Creating an Executable
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