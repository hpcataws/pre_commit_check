"""lints for programming languages: Swift, Rust, Python, Make"""
import shutil
import os
from pathlib import Path
import sys
import subprocess
from typing import final

from pre_commit_check.lint import Lint
from pre_commit_check.git import print_short_status

SCRIPTS = ["codecommit-tags.py", "rusage.py", "aws-creds-role.py",
           "precommit-check.py", "git-log.py", "main_log.py"]


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
