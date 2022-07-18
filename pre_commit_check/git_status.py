"""utilities for the git status of files."""

from abc import ABC, abstractmethod
import subprocess


class GitStatusABC(ABC):

    @abstractmethod
    def print_short_status(self, url: str) -> None:
        pass


class GitStatus(GitStatusABC):

    def print_short_status(self, url: str) -> None:
        """Print short version of git status."""
        try:
            subprocess.run(["git", "status", "-s", url], check=True)
        except subprocess.CalledProcessError as error:
            print(f"git status failed {error}")
