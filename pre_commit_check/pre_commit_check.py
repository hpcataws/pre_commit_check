#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module lints my LaTeX, C, C++, Rust, Swift code, my git repository,
and my Python scripts before a git commit
"""

__version__ = '0.1'
__author__ = "T. Schütt <schuett@gmail.com>"
__doc__ = "Lints the main.tex file before a git commit"

#from abc import abstractmethod
#import collections
#import collections.abc
#from contextlib import contextmanager
import fileinput
#from functools import cache
import logging
from pathlib import Path
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

log = logging.getLogger(__name__)

# pylint, mypy, pytype

# the input and output files of the last latex command are in main.fls

SCRIPTS = ["codecommit-tags.py", "rusage.py", "aws-creds-role.py",
           "precommit-check.py", "git-log.py", "main_log.py"]

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
class SwiftLint(Lint):
    """Lint the Swift code"""

    @staticmethod
    def run_swift(_root: str) -> None:
        """Run swift on the Swift code"""
        if shutil.which("swift"):
            try:
                subprocess.run(["swift", "package", "clean"], check=True)
                subprocess.run(
                    ["swift", "build", "-Xswiftc", "-warnings-as-errors"],
                    check=True)
            except subprocess.CalledProcessError as error:
                print(f"swift build failed: {error}")
                sys.exit(-1)

    @staticmethod
    def run_swift_lint(root: str) -> None:
        """Run swiftlint on the Swift code"""
        if shutil.which("swiftlint"):
            working_directory = os.getcwd()
            os.chdir(root)
            try:
                subprocess.run(["swiftlint", "lint", "Sources"], check=True)
            except subprocess.CalledProcessError as error:
                print(f"swiftlint failed: {error}")
                sys.exit(-1)
            os.chdir(working_directory)

    @staticmethod
    def run_swift_format(root: str) -> None:
        """Run swift format and lint on the Swift code"""
        if shutil.which("swift-format"):
            working_directory = os.getcwd()
            os.chdir(root)
            try:
                subprocess.run(
                    ["swift-format", "format", "-i", "-r", "Sources"],
                    check=True)
                subprocess.run(
                    ["swift-format", "lint", "-r", "Sources"], check=True)
            except subprocess.CalledProcessError as error:
                print(f"swift-format failed: {error}")
                sys.exit(-1)
            os.chdir(working_directory)

    def run(self, root: str) -> None:
        package_file = Path(root + "/Package.swift")
        if package_file.is_file():
            print_short_status(os.fspath(package_file))
            print("swift repo")

            SwiftLint.run_swift_lint(root)
            SwiftLint.run_swift_format(root)
            SwiftLint.run_swift(root)


@final
class RustLint(Lint):
    """Lint the Rust code"""

    def run(self, root: str) -> None:
        package_file = Path(root + "/Cargo.toml")
        if package_file.is_file():
            if shutil.which("cargo"):
                # subprocess.run(["cargo", "clean"])
                try:
                    subprocess.run(
                        ["cargo", "clippy", "--", "-D", "warnings"],
                        check=True)
                except subprocess.CalledProcessError as error:
                    print(f"cargo clippy failed: {error}")
                    sys.exit(-1)
                print_short_status(os.fspath(package_file))
                print("rust repo")


@final
class PythonLint(Lint):
    """Check the git status of the Python scripts"""

    def run(self, root: str) -> None:
        for script in SCRIPTS:
            print_short_status(script)


@final
class MakeLint(Lint):
    """Lint C++ code with a Makefile"""

    def run(self, root: str) -> None:
        package_file = Path(root + "/code/Makefile")
        if package_file.is_file():
            working_directory = os.getcwd()
            os.chdir(root + "/code")
            try:
                subprocess.run(["make", "clean"], check=True)
                subprocess.run(["make"], check=True)
            except subprocess.CalledProcessError as error:
                print(f"make failed: {error}")
                sys.exit(-1)
            os.chdir(working_directory)


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
