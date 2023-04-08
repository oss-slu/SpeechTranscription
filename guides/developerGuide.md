# Contributing as a Developer

## Development Environment
1. **Clone the Repository** - [This link](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) details how you can create a local clone of the repository. To do this, you need to have Git installed. Information for installing Git can be found [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
2. **Requirements** - This project uses Python, which can be downloaded [here](https://www.python.org/downloads/). Before attempting to run GUI.py with "python GUI.py" in your command line interface, you should install all the packages found in [requirements.txt](https://github.com/oss-slu/SpeechTranscription/blob/userGuides/requirements.txt). For example, typing "pip install git+https://github.com/openai/whisper.git" will install the whisper package, which we use for speech recognition.
    *   It may be beneficial to create a python virtual environment that contains only the packages required for this project. This allows you to isolate your development environment to be specialized for this project.
3. **Running the Program** - Simply type "python GUI.py" in the command line while in the repository to start the program.

## Using GitHub Issues when Adding Features and Fixing Bugs

- Use the [issues](https://github.com/oss-slu/SpeechTranscription/issues) page to keep track of changes that need to be made regarding features, documentation, and bugs. There is also a [board](https://github.com/orgs/oss-slu/projects/11) page which displays the issues in an easier to read manner.
- To contribute to the project, first either pick an issue or create a new issue, then create a new branch off of main that will be dedicated to that issue. For example, if I wanted to make a new branch, I would do "git checkout main", "git pull", "git branch (new branch name)", and "git checkout (new branch name)". Then, make changes you want to the code, commit them to the branch, and push them upstream. Once you believe your branch is ready to be merged to main, make a pull request.

## Creating an Executable
- TODO