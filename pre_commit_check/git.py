"""Utilities for working with git repositories."""

from abc import ABC, abstractmethod
import errno
from functools import cache            # 3.9
import subprocess
import sys
from typing import final

from git import Repo
import git

from pre_commit_check.utilities import get_root

REGION = "eu-central-1"


class GitRemoteUrlABC(ABC):

    @abstractmethod
    def get_remote_url(self) -> str:
        pass


class GitRemoteUrl(GitRemoteUrlABC):

    @cache
    def get_remote_url(self) -> str:
        """Get git remote url."""
        try:
            return subprocess.run(["git", "config", "--get",
                                   "remote.origin.url"], check=True, encoding="utf-8",
                                  stdout=subprocess.PIPE).stdout.strip()
        except subprocess.CalledProcessError as error:
            print("git config --get remote.origin.url failed")
            print("Is this really a git repository?")
            print(error)
            sys.exit(-1)


def is_github_repo(git_remote_url: GitRemoteUrlABC) -> bool:
    """Check if the local repo is a GitHub repo."""
    # remote_url = git_remote_url.get_remote_url()
    return "@github.com:" in git_remote_url.get_remote_url()


def is_default_branch_main() -> bool:
    """Check if the default branch is main."""
    try:
        lines = subprocess.run(["git", "remote", "show", "origin"], check=True,
                               encoding="utf-8",
                               stdout=subprocess.PIPE).stdout.splitlines()
        for line in lines:
            if "HEAD branch" in line:
                default = line.split(':')[1].removeprefix(' ')
                if default == "main":
                    return True

        print(lines)
        return False
    except subprocess.CalledProcessError as error:
        print("git remote show origin failed")
        print("Is this really a git repository?")
        print(error)
        print(f"stdout    : x{error.stdout}x")
        print(f"stderr    : x{error.stderr}x")
        print(f"returncode: x{error.returncode}x")
        print(f"returncode: x{errno.errorcode[error.returncode]}x")
        sys.exit(-1)


@final
class GitWrapper:
    """Wrapper around GitPython."""

    def __init__(self):
        """Run the constructor."""
        self.__repo = Repo(get_root())

    def get_origin_url(self) -> str:
        """Get the remote origin url."""
        return self.__repo.remotes.origin.url

    def get_head_sha(self) -> str:
        """Get the hexsha of the commit of the HEAD object."""
        return self.__repo.head.commit.hexsha

    def get_origin_head_sha(self) -> str:
        """Get a remote tracking branch."""
        return self.__repo.refs['origin/main'].commit.hexsha

    def get_remote_origin_head_sha(self) -> str:
        """Get the remote head commit sha."""
        url = self.get_origin_url()
        ref = git.cmd.Git().ls_remote(url, heads=True)
        return ref.split('\t')[0]

    def get_nr_of_local_commits(self) -> int:
        """Get the list of local commits."""
        return len(list(self.__repo.iter_commits('origin/main..HEAD')))
