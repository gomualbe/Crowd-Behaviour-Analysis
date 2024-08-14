# Crowd-Behaviour-Analysis

### Python Version
This project uses Python 3.12.4. You can create a new virtual environment with this version by running the following:
```bash
conda create -n Crowd-Behaviour-Analysis python=3.12.4  # Create a new conda environment
conda activate Crowd-Behaviour-Analysis  # Activate the environment
pip install -r requirements.txt  # Install the required packages
```

## Running the project
Before running the project, make sure to setup correctly the `camera_links.txt` file. You can find it in the main 
directory of the project.\
This file should contain the links to the cameras that you want to use.
If camera links are not working, try to add '/video' at the end of the link. \
\
To run the project, you can run the main file by running the following command:
```bash
python main.py
```

### After running the project
After runnign the project you can see on the left a sidebar with a scroll area with all the cameras that you have 
added in the previous step. \
By selecting one of them you can change the camera that you are currently viewing (the first one by default when you 
run the project) on the right side of the screen, which is also the camera that is being analyzed by the Crowd 
Analysis system in real-time. 