#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module lints my LaTeX, C, C++, Rust, Swift code, my git repository,
and my Python scripts before a git commit
"""

__version__ = '0.1'
__author__ = "T. Schütt <schuett@gmail.com>"
__doc__ = "Lints the main.tex file before a git commit"

import logging
import os
import shutil
import subprocess
import sys

from pre_commit_check.bibtex import BibTeXLint
from pre_commit_check.git import is_default_branch_main
from pre_commit_check.local_git import LocalGit
from pre_commit_check.utilities import get_root
from pre_commit_check.languages import SwiftLint, RustLint, PythonLint, MakeLint
from pre_commit_check.latex import LaTexLint
from pre_commit_check.missing_labels import MissingLabelsLint
from pre_commit_check.cmake import CMakeLint
from pre_commit_check.git_status import GitStatus

log = logging.getLogger(__name__)

# pylint, mypy, pytype

# the input and output files of the last latex command are in main.fls

"""Checks invariants and lints before running git commit"""


def primary_checks() -> int:
    """Primary checks."""
    if not sys.version_info >= (3, 9):
        print("This script requires Python 3.9 or higher!")
        print("You are using Python {}.{}.".format(
            sys.version_info.major, sys.version_info.minor))
        return 1

    if not os.path.exists("main.tex"):
        print("there is no main.tex")
        print("this configuration is not supported")
        return 1

    if not shutil.which("latexmk"):
        print("there is no latexmk")
        print("this configuration is not supported")
        return 1

    if not is_default_branch_main():
        print("default branch is not main")
        print("this configuration is not supported")
        return 1

    return 0


def main() -> int:
    """Define the main function."""
    if primary_checks() != 0:
        return 1

    try:
        subprocess.run(["latexmk", "-C"], check=True)
    except subprocess.CalledProcessError as error:
        print(f"latexmk -C failed: {error}")
        return 1

    try:
        subprocess.run(["latexmk", "-time", "-pdf",
                        "-interaction=nonstopmode",
                        "-Werror", "-logfilewarninglist", "main"],
                       check=True)
    except subprocess.CalledProcessError as error:
        print(f"latexmk failed; please check main.log: {error}")
        return 1

    root = get_root()
    git_status = GitStatus()

    lints = [PythonLint(), LaTexLint(), BibTeXLint(), SwiftLint(), RustLint(),
             LocalGit(), MakeLint(), CMakeLint(), MissingLabelsLint()]
    for lint in lints:
        lint.run(root, git_status)

    return 0


if __name__ == '__main__':
    sys.exit(main())
