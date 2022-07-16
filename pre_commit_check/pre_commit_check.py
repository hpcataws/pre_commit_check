#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module lints my LaTeX, C, C++, Rust, Swift code, my git repository,
and my Python scripts before a git commit
"""

__version__ = '0.1'
__author__ = "T. Schütt <schuett@gmail.com>"
__doc__ = "Lints the main.tex file before a git commit"

from abc import ABC, abstractmethod
import collections
import collections.abc
from contextlib import contextmanager
import fileinput
from functools import cache
import logging
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
from typing import final

import bibtexparser  # type: ignore
import botocore      # type: ignore
import boto3         # type: ignore
from git import Repo
import git

log = logging.getLogger(__name__)

# pylint, mypy, pytype

# the input and output files of the last latex command are in main.fls

SCRIPTS = ["codecommit-tags.py", "rusage.py", "aws-creds-role.py",
           "precommit-check.py", "git-log.py", "main_log.py"]

REGION = "eu-central-1"

"""Checks invariants and lints before running git commit"""


@cache
def get_remote_url() -> str:
    """get git remote url"""
    try:
        return subprocess.run(["git", "config", "--get",
                               "remote.origin.url"], check=True, encoding="utf-8",
                              stdout=subprocess.PIPE).stdout.strip()
    except subprocess.CalledProcessError as error:
        print("git config --get remote.origin.url failed")
        print("Is this really a git repository?")
        print(error)
        sys.exit(-1)


def is_aws_codecommit_repo() -> bool:
    """check if the local repo is a AWS CodeCommit repo"""
    remote_url = get_remote_url()
    url_git = f"git-codecommit.{REGION}.amazonaws.com/v1/repos"
    url_http = f"codecommit::{REGION}://"
    if url_git in remote_url:
        return True
    if url_http in remote_url:
        return True

    return False


def is_github_repo() -> bool:
    """check if the local repo is a GitHub repo"""
    remote_url = get_remote_url()
    return "@github.com:" in remote_url


def is_default_branch_main() -> bool:
    """check if the default branch is main"""
    try:
        lines = subprocess.run(["git", "remote", "show", "origin"], check=True,
                               encoding="utf-8", stdout=subprocess.PIPE).stdout.splitlines()
        for line in lines:
            if "HEAD branch" in line:
                default = line.split(':')[1].removeprefix(' ')
                if default == "main":
                    return True

        return False
    except subprocess.CalledProcessError as error:
        print("git remote show origin failed")
        print("Is this really a git repository?")
        print(error)
        sys.exit(-1)


def check_default_branch_main_boto3() -> None:
    """check if the default branch is main"""
    try:
        client = boto3.client('codecommit')
        remote_url = get_remote_url()
        repo_name = remote_url.split('/')[-1]
        default_branch = client.get_repository(repositoryName=repo_name)[
            'repositoryMetadata']['defaultBranch']
        if default_branch != 'main':
            print(f"default branch is not main: {default_branch}")
            print("this configuration is not supported")
            sys.exit(-1)
    except botocore.exceptions.ClientError as error:
        print(f"no AWS credentials: {error}")
    except botocore.exceptions.EndpointConnectionError as error:
        print(f"endpoint connection failed: {error}")


class Lint(ABC):
    """Base class for lints"""

    @abstractmethod
    def run(self, root: str) -> None:
        """abstract function for running lints"""


@final
class GitWrapper:
    """Wrapper around GitPython and AWS CodeCommit"""

    def __init__(self):
        self.repo = Repo(get_root())

    def get_origin_url(self) -> str:
        """the remote origin url"""
        return self.repo.remotes.origin.url

    def get_head_sha(self) -> str:
        """the hexsha of the commit of the HEAD object"""
        return self.repo.head.commit.hexsha

    def get_origin_head_sha(self) -> str:
        """ a remote tracking branch"""
        return self.repo.refs['origin/main'].commit.hexsha

    def get_remote_origin_head_sha(self) -> str:
        """the remote head commit sha"""
        url = self.get_origin_url()
        ref = git.cmd.Git().ls_remote(url, heads=True)
        return ref.split('\t')[0]

    def get_nr_of_local_commits(self) -> int:
        """the list of local commits"""
        return len(list(self.repo.iter_commits('origin/main..HEAD')))


def print_short_status(url: str) -> None:
    """print short version of git status"""
    try:
        subprocess.run(["git", "status", "-s", url], check=True)
    except subprocess.CalledProcessError as error:
        print(f"git status failed {error}")


@final
class CodeCommit(Lint):
    """Lint AWS CodeCommit and local git"""

    # git rev-parse origin/HEAD # to get the latest commit on the remote

    # git rev-parse HEAD          # to get the latest commit on the local

    # git config --get remote.origin.url

    # git ls-remote -h `git config --get remote.origin.url`

    def __init__(self):
        self.git_wrapper = GitWrapper()

    def run(self, root: str) -> None:
        head_sha = self.git_wrapper.get_head_sha()
        upstream_sha = self.git_wrapper.get_origin_head_sha()
        if head_sha != upstream_sha:
            print(
                f"git: local commits {self.git_wrapper.get_nr_of_local_commits()}")
        if self.git_wrapper.get_remote_origin_head_sha() != upstream_sha:
            print("git: upstream changes")


@final
class MainFlsLines(collections.abc.Iterator):
    """line iterator over main.fls"""

    def __init__(self, file_descriptor):
        self.file_descriptor = file_descriptor

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            line = self.file_descriptor.readline()
            if not line:
                raise StopIteration
            if line.startswith("INPUT ") and not line.startswith("INPUT /usr/local"):
                return line.removeprefix("INPUT ").removesuffix("\n")


@contextmanager
def main_fls():
    """context manager for main.fls"""
    with open("main.fls", "r") as file_descriptor:
        try:
            yield MainFlsLines(file_descriptor)
        finally:
            pass


@final
class BibTeXLint(Lint):
    """Lint bib files and citations of main.tex """

    @staticmethod
    def get_citations() -> set[str]:
        """Return the bibtex entries cited by main.tex"""
        citations = set()
        with fileinput.input(files=("main.aux")) as file_input:
            for line in file_input:
                if line.startswith("\citation{"):
                    cites = line.removeprefix("\citation{").removesuffix("}\n")
                    split = cites.split(',')
                    for cite in split:
                        citations.add(cite)
        return citations

    # bib files are not input files for latex. they are inputs for bibtex
    @staticmethod
    def get_bib_files() -> set[str]:
        """Return the bib files needed by main.tex"""
        bib_files: set[str] = set()
        bbl_files: list[str] = []
        with main_fls() as fls_file:
            for line in fls_file:
                if line.endswith(".bbl"):
                    bbl_files.append(line.removeprefix("./"))

        if not bbl_files:
            return set()

        blg_files = map(lambda bbl: os.path.splitext(bbl)[
                        0]+'.blg', sorted(set(bbl_files)))
        with fileinput.input(files=list(blg_files)) as file_input:
            for line in file_input:
                if line.startswith("Database file"):
                    split = line.split(':')
                    file = line.removeprefix(
                        split[0]+": ").removesuffix("\n")
                    bib_files.add(file)
        return bib_files

    def check_bib_files(self) -> None:
        """Check the git status of the bib files of main.tex"""
        for bib_file in self.get_bib_files():
            print_short_status(bib_file)

    @staticmethod
    def check_citations() -> None:
        """Check for duplicate bib entries"""
        citations = BibTeXLint.get_citations()
        for bib_file in BibTeXLint.get_bib_files():
            with open(bib_file) as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
                for entry in bib_database.entries:
                    if not entry['ID'] in citations:
                        entry_id = entry['ID']
                        print(f"remove {entry_id:20} from {bib_file}")
                        sys.exit(-1)

    def run(self, root: str) -> None:
        if not os.path.exists("main.fls"):
            print("main.fls is missing")
            sys.exit(1)

        self.check_bib_files()
        BibTeXLint.check_citations()


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


@cache
def get_root() -> str:
    """Return the root path of the git repository"""

    try:
        return subprocess.run(["git", "rev-parse",
                               "--show-toplevel"], check=True, encoding="utf-8",
                              stdout=subprocess.PIPE).stdout.strip()
    except subprocess.CalledProcessError as error:
        print("git rev-parse --show-toplevel failed")
        print("Is this really a git repository?")
        print(error)
        sys.exit(-1)


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
