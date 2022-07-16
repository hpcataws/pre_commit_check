#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module lints my LaTeX, C, C++, Rust, Swift code, my git repository,
and my Python scripts before a git commit
"""

__version__ = '0.1'
__author__ = "T. Schütt <schuett@gmail.com>"
__doc__ = "Lints the main.tex file before a git commit"

import fileinput
import logging
import os
import re
import shutil
import subprocess
import sys
from typing import final

# import bibtexparser  # type: ignore
# import botocore      # type: ignore
# import boto3         # type: ignore

from pre_commit_check.bibtex import BibTeXLint
from pre_commit_check.lint import Lint
from pre_commit_check.fls_file import main_fls
from pre_commit_check.git import is_aws_codecommit_repo, is_default_branch_main, print_short_status, CodeCommit, check_default_branch_main_boto3
from pre_commit_check.utilities import get_root

from pre_commit_check.languages import SwiftLint, RustLint, PythonLint, MakeLint

log = logging.getLogger(__name__)

# pylint, mypy, pytype

# the input and output files of the last latex command are in main.fls

"""Checks invariants and lints before running git commit"""


@final
class LaTexLint(Lint):
    """Lint input files of main.tex """

    @staticmethod
    def check_input_files() -> None:
        """Check the git status of the input files of main.tex"""
        files: list[str] = []
        with main_fls() as fls_file:
            for line in fls_file:
                files.append(line.removeprefix("./"))
        input_files: list[str] = sorted(set(files))

        for file in input_files:
            print_short_status(file)

    def run(self, root: str) -> None:
        if not os.path.exists("main.fls"):
            print("main.fls is missing")
            sys.exit(1)

        LaTexLint.check_input_files()


@final
class MissingLabelsLint(Lint):
    """Lint labels"""

    def run(self, root: str) -> None:
        labels = set()
        mainlabels = set()
        with fileinput.input(files=("main.aux")) as file_input:
            for line in file_input:
                if line.startswith("\\newlabel{"):
                    first = line.removeprefix("\\newlabel{")
                    label = first.split('}')[0]
                    if label.startswith("fig.") or label.startswith("sec."):
                        labels.add(label)

        with fileinput.input(files=("main.tex")) as file_input:
            for line in file_input:
                idxs = [m.start() for m in re.finditer('figref', line)]
                for idx in idxs:
                    label = line[idx:-1].removeprefix("figref{")
                    label = label.split('}')[0]
                mainlabels.add(label)
                idxs = [m.start() for m in re.finditer('secref', line)]
                for idx in idxs:
                    label = line[idx:-1].removeprefix("secref{")
                    label = label.split('}')[0]
                    mainlabels.add(label)

        print(f"uncited label: {labels-mainlabels}")


def primary_checks() -> int:
    """primary checks"""
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

    if not is_aws_codecommit_repo():
        print("this is no AWS CodeCommit respository")
        print("this configuration is not supported")
        return 1

    if not is_default_branch_main():
        print("default branch is not main")
        print("this configuration is not supported")
        return 1

    return 0


def main() -> int:
    """the main function"""

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

    check_default_branch_main_boto3()

    root = get_root()

    lints = [PythonLint(), LaTexLint(), BibTeXLint(), SwiftLint(), RustLint(),
             CodeCommit(), MakeLint(), MissingLabelsLint()]
    for lint in lints:
        lint.run(root)

    return 0


if __name__ == '__main__':
    sys.exit(main())
