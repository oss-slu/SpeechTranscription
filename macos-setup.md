## Developer's Guide for Setting Up MacOS Environment

Ensure you have the following prerequisites downloaded:

* `Java` --> [Download Here](https://www.oracle.com/java/technologies/downloads/)
* `MySQL` --> [Download Here](https://dev.mysql.com/downloads/mysql/)

Once those are downloaded and you have cloned the Git repository, you will want to go into the SpeechTranscription directory and create/activate a Python virtual environment:

* `python3 -m venv venv` to create the environment.
* `source venv/bin/activate` to activate.

In order to install the dependencies from the requirements file, you will need to manually set the environment variables for mySQL. Enter these commands in your terminal:

* `export MYSQLCLIENT_CFLAGS='pkg-config mysqlclient --cflags'`
* `export MYSQLCLIENT_LDFLAGS='pkg-config mysqlclient --libs'`

Afterwards, enter the following command to install Homebrew for MacOS:

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

Note: After installation, Homebrew will prompt you to set up environment variables. Ensure you follow those instructions before proceeding.

Once Homebrew is set up and installed, you can enter the following commands:

* `brew install mysql pkg-config`
* `brew install portaudio`
* `pip install pyaudio`

Now you may run the `pip install -r requirements.txt` command to install the requirement dependencies.

If installing requirements.txt file still won't run, then you may need to use the `pip3 install mysql-connector-python` command.

The 'nltk' library installation is more complex on MacOS.

    1. Install nltk and certifi via pip:
        pip install nltk
        pip3 install certifi

    2. Enter the following commands to avoid SSL Certificate issues:
        CERT_PATH=$(python -m certifi)
        export SSL_CERT_FILE=${CERT_PATH}
        export REQUESTS_CA_BUNDLE=${CERT_PATH}

    3. Open Python Interpreter and import/download nltk:
        >>> import nltk
        >>> nltk.download()

    This is a temporary fix to use the nltk library for your current terminal session on MacOS. If you want to make these changes permanent, you must add the commands from step 2 to your .bash_profile.

Finally, after running `git submodule init`, you should be able to run the program using `python GUI.py`.