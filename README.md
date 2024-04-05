# Crowd-Behaviour-Analysis

## Python Version
This project uses Python 3.12.2. You can download this version from [here](https://www.python.org/downloads/release/python-3122/).

## Install virtualenv
For the current project, we will be using a virtual environment. To install virtualenv, if you are in a __Linux__ or __macOS__ systems run the following command inside the project directory:
```bash
python3 -m venv env
source env/bin/activate
```

If you are in a __Windows__ system, run the following command:
```bash
python3 -m venv env
.\env\Scripts\activate
```

After running the above commands, you should see `(env)` in your terminal. This means that you are in the virtual environment.

Now that you are in the virtual environment, you can install the requirements by running the following command:
```bash
pip3 install -r requirements.txt
```
\
After that make sure to add a `.gitignore`, if you haven't already, with the following command:
```bash
echo "/env" >> .gitignore
```