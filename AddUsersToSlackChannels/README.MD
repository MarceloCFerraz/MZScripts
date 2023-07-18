# Slack Bot

This project aims to help production support team members from MileZero to bulk-add users to their respective slack channels by automating screen interactions such as clicks, key presses and typing.

## How to use it

There are a couple of dependencies that need to be installed first but the use itself is very simple and straightforward

You must create a `accounts.xlsx` file that must contain both the e-mails to be added AND the name/reference of the slack channel that should get this new user invited.

The file mentioned above must follow the structure found on `model.xlsx` that can be found on this project folder

## Install Dependencies

### Pyenv

You may want to take a look at [Pyenv](https://github.com/pyenv/pyenv) or [Pyenv for Windows](https://github.com/pyenv-win/pyenv-win). It's like NVM but for Python.

If you decided to go with Pyenv, just like NVM, remember to unninstall any python installations you may have before installing Pyenv.

### Python

This project uses Python 3.11.2. You can click [here](https://www.python.org/downloads/release/python-3112/) to download and install it or use `pyenv install 3.11.2` and `pyenv local 3.11.2`

### Pip

Pip is a python package manager just like npm. Usually, python already comes with Pip but if hasn't in your case, open the command prompt and run `python -m ensurepip --upgrade`

### Virtualenv

Virtualenv will take care to install the project dependencies only to the project folder.
To install virtualenv, open the command prompt and run `pip install virtualenv`

After that, open a command prompt at the project folder and run `virtualenv venv`

### Activate venv

On Unix or MacOS, using the bash shell run `source venv/bin/activate`

On Unix or MacOS, using the csh shell: run `source venv/bin/activate.csh`

On Unix or MacOS, using the fish shell: run `source venv/bin/activate.fish`

On Windows using the Command Prompt: run `source venv/bin/activate.bat`

On Windows using PowerShell: run `source venv/bin/Activate.ps1`

### Install dependencies

With the venv activated, run `pip install -r requirements.txt`

### Run

Now you should be able to run the project on the console with `python main.py`
