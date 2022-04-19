# Learning Hints for Automated Planning
#### Deep reinforcement learning to improve performance of a classical planner by generating "hints," or actions that are likely part of a valid plan.

## Environment

It is recommended but not required to install the required python modules (see requirements.txt) in a virtual environment.
If the instructions in the "Running" section do not work for you, try the following steps (All from the base directory of the project)

Leave any current virtual python environment you are in, e.g.
```
deactivate
```
or
```
conda deactivate
```
Create an empty virtual environment
```
python3 -m venv env
```
Enter the virtual environment
```
source env/bin/activate
```
Install the required libraries
```
pip3 install -r requirements.txt
```
When you are done working with the project, leave the virtual environment
```
deactivate
```
