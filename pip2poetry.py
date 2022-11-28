#!/usr/bin/env python3
"""
Copies the packages listed in requirements.txt file to pyproject.toml.
Copies the packages listed in 'install_requires' section of the setup.py to pyproject.toml
Writes the poetry.lock file.

Usage:
Copy the script to the same directory as that of the setup.py file.

Run!
"""
import os
import setuptools
import runpy
import sys
import re

from pathlib import Path
from unittest.mock import Mock
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType


pipPoetryMap = {
        ">": "^",
        "=": ""
    }

# TODO: Collect errors/failures and display in the end of the execution.
ERRORS = []

def find_files(filename='requirements.txt', search_path=os.getcwd()):
    """Returns a list of paths of the file 'filename' found in the 
       directory path 'search_path'.
    """
    result = []
    for root, _, files in os.walk(search_path):
      if filename in files:
        result.append(os.path.join(root, filename))
    return result 

def get_requirements(requirements, pipPoetryMap):
    """Returns a list of dependencies in poetry usable format name:=version when provided by
        a list of requirements in the format `name==version`.
    """
    reqList = list()
    for line in requirements:
        package, match, version = re.sub(r"^(.*?)\s*([~>=<])=\s*v?([0-9\.\*]+)", r"\1,\2,\3", line, 0, re.IGNORECASE | re.MULTILINE).split(",")
        try:
            poetryMatch = pipPoetryMap[match]
        except KeyError:
            poetryMatch = match
        poetryLine = f"{package}=={poetryMatch}{version}"
        reqList.append(poetryLine)
    return reqList

def parse_setup_py(setup):
    options = {}
    setif(setup, options, 'install_requires')
    return options

def run_setup(setup_py: Path):
    global setuptools
    sys.modules['setuptools'] = Mock(spec=setuptools)
    import setuptools
    runpy.run_path(setup_py, {}, "__main__")
    return setuptools.setup.call_args[1]

def setif(src, dest, key, type_cast=None):
    if key in src:
        dest[key] = type_cast(src[key]) if type_cast else src[key]

def main(cli_args=None):
    args = parse_args(cli_args)
    setup_py = Path(args.setup_py.name).resolve()
    # Initialize Poetry if it doesn't yet have a pyproject.toml file
    if not os.path.exists("./pyproject.toml"):
        # Remove `-n` argument from the command for poetry interactive input.
        os.system("poetry init -n")

    if os.path.exists(setup_py):
        # Extracts main dependencies from setup.py file
        requirements = parse_setup_py(run_setup(setup_py))['install_requires']
        reqList = get_requirements(requirements, pipPoetryMap)
        reqList = " ".join(reqList)
        print(reqList)
        os.system(f"poetry add {reqList} --lock")

    req_txts = find_files()
    for req_txt in req_txts:
        # Extracts dev dependencies from requirements.txt file
        with open(req_txt) as fh:
            requirements = fh.read()
        requirements = [line for line in requirements.splitlines() if not line.strip().startswith('#')]
        reqList = get_requirements(requirements, pipPoetryMap)
        reqList = " ".join(reqList)
        print(reqList)
        os.system(f"poetry add {reqList} --group dev --lock")

def parse_args(args=None):
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, description=__doc__)
    parser.add_argument(
        'setup_py', type=FileType('r'), default='./setup.py', nargs='?', metavar='path',
        help='path to setup.py file')

    return parser.parse_args(args)

if __name__ == '__main__':
    # TODO: Add Poetry Specific Exception handling.
    try:
        main()
        if ERRORS:
            print(ERRORS)
    except Exception as ex:
        print(ex)
