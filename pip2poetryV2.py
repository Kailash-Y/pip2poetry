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
    setup_py = Path(args.setup_py)
    # Initialize Poetry if it doesn't yet have a pyproject.toml file
    init_path = Path("./pyproject.toml")
    if init_path.exists():
        os.system(f"rm -f {init_path}")
    poetry_init(python_version=args.version)

    if setup_py.exists():
        # Extracts main dependencies from setup.py file
        requirements = parse_setup_py(run_setup(setup_py))['install_requires']
        reqList = get_requirements(requirements, pipPoetryMap)
        reqList = " ".join(reqList)
        print(reqList)
        os.system(f"poetry add {reqList} --lock")

    for req_txt in args.requirements:
        req_txt = Path(req_txt)
        if not req_txt.exists():
            print(f"Error: The Path {req_txt} does not exist")
            exit(1)
        # Extracts dev dependencies from requirements.txt file
        with open(req_txt) as fh:
            requirements = fh.read()
        requirements = [line for line in requirements.splitlines() if not line.strip().startswith('#')]
        reqList = get_requirements(requirements, pipPoetryMap)
        reqList = " ".join(reqList)
        print(reqList)
        os.system(f"poetry add {reqList} --group dev --lock")

def poetry_init(python_version):
    import pexpect
    p = pexpect.spawn("poetry init")
    p.expect(".*Package name.*:")
    p.sendline("Project")
    p.expect(".*Version.*:")
    p.sendline("1.0.0")
    p.expect(".*Description.*:")
    p.sendline("None")
    p.expect(".*Author.*:")
    p.sendline("n")
    p.expect(".*License.*:")
    p.sendline("None")
    p.expect(".*Compatible Python versions.*:")
    p.sendline(python_version)
    p.expect(".*Would you like to define your main dependencies interactively.*")
    p.sendline("no")
    p.expect(".*Would you like to define your development dependencies interactively.*")
    p.sendline("no")
    p.expect(".*Do you confirm generation.*")
    p.sendline("yes")
    p.expect(pexpect.EOF)

def parse_args(args=None):
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, description=__doc__)
    parser.add_argument('--requirements', '-r', default='./tests/requirements.txt', nargs='*', 
        metavar='requirements', help='List of paths to requirement.txt')
    parser.add_argument(
        '--setup_py', '-s', default='./setup.py', nargs='?', metavar='path',
        help='path to setup.py file')
    parser.add_argument(
        '--version', '-v', nargs='?', default='^3.5', metavar='python_version',
        help='Compatible Python versions')

    return parser.parse_args(args)

if __name__ == '__main__':
    # TODO: Add Poetry Specific Exception handling.
    try:
        main()
        if ERRORS:
            print(ERRORS)
    except Exception as ex:
        print(ex)
