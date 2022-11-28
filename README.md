# pip2poetry
Move from pip to poetry using this script

Features:
========
1. Extracts the dependencies/packages from the "install_requires" section of setup.py and adds them to the poety's pyproject.toml file.
2. Extracts the dependencies/packages from "requirements.txt" lying anywhere inside the working directory  and adds them to the poety's pyproject.toml file.
3. Writes the Poetry.lock file.

Usage:
======
pip2poetry <setup_py_file_path> 

default path: "./setup.py"

