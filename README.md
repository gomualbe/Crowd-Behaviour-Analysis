# Crowd-Behaviour-Analysis

### Python Version
This project uses Python 3.12.2. You can download this version from [here](https://www.python.org/downloads/release/python-3122/).

## Install virtualenv
For the current project, we will be using a virtual environment. To install virtualenv, if you are in a __Linux__ or 
__macOS__ systems run the following command inside the project directory:
```bash
python3 -m venv env
source env/bin/activate
```

If you are in a __Windows__ system, run the following command:
```bash
python3 -m venv env
.\env\Scripts\activate
```

After running the above commands, you should see `(env)` in your terminal. This means that you are in the
virtual environment.

Now that you are in the virtual environment, you can install the requirements by running the following command:
```bash
pip3 install -r requirements.txt
```

## Running the project
Before running the project, make sure to setup correctly the `camera_links.txt` file. You can find it in the main 
directory of the project. This file should contain the links to the cameras that you want to use. \
\
To run the project, you can run the main file by running the following command:
```bash
python3 main.py
```

### After running the project
After runnign the project you can see on the left a sidebar with a scroll area with all the cameras that you have 
added in the previous step. \
By selecting one of them you can change the camera that you are currently viewing (the first one by default when you 
run the project) on the right side of the screen, which is also the camera that is being analyzed by the Crowd 
Analysis system in real-time. 