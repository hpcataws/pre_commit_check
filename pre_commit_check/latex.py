"""checks the git status of the input of main.tex."""

import os
import sys
from typing import final

from pre_commit_check.fls_file import main_fls
from pre_commit_check.lint import Lint
from pre_commit_check.git_status import GitStatusABC


@final
class LaTexLint(Lint):
    """Lint input files of main.tex."""

    @staticmethod
    def check_input_files(git_status: GitStatusABC) -> None:
        """Check the git status of the input files of main.tex."""
        files: list[str] = []
        with main_fls() as fls_file:
            for line in fls_file:
                files.append(line.removeprefix("./"))
        input_files: list[str] = sorted(set(files))

        for file in input_files:
            git_status.print_short_status(file)

    def run(self, root: str, git_status: GitStatusABC) -> None:
        """Run the latex lint: check for input files."""
        if not os.path.exists("main.fls"):
            print("main.fls is missing")
            sys.exit(1)

        LaTexLint.check_input_files(git_status)
