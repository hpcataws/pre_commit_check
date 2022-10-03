"""lint using cmake."""

from pathlib import Path
import os
import subprocess
import sys
from typing import final

from pre_commit_check.lint import Lint
from pre_commit_check.git_status import GitStatusABC


@final
class CMakeLint(Lint):
    """Lint the C/C++ code built with CMake."""

    def run(self, root: str, git_status: GitStatusABC) -> None:
        """Lint C/C++ code."""
        cmake_lists_file = Path(root + "/CMakeLists.txt")
        if cmake_lists_file.is_file():
            working_directory = os.getcwd()
            os.chdir(root)
            try:
                subprocess.run(["cmake", "."], check=True)
                subprocess.run(["make"], check=True)
            except subprocess.CalledProcessError as error:
                print(f"cmake failed: {error}")
                sys.exit(-1)

            os.chdir(working_directory)
