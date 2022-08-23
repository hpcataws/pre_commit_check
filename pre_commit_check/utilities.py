"""get the root of the git checkout."""

from functools import cache       # 3.9
import subprocess
import sys


@cache
def get_root() -> str:
    """Return the root path of the git repository."""
    try:
        return subprocess.run(["git", "rev-parse",
                               "--show-toplevel"],
                              check=True, encoding="utf-8",
                              stdout=subprocess.PIPE).stdout.strip()
    except subprocess.CalledProcessError as error:
        print("git rev-parse --show-toplevel failed")
        print("Is this really a git repository?")
        print(error)
        sys.exit(-1)
