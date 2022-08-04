"""Utilities for working with git repositories."""

from abc import ABC, abstractmethod
from functools import cache            # 3.9
import subprocess
import sys
from typing import final

import botocore      # type: ignore
import boto3         # type: ignore
from git import Repo
import git

from pre_commit_check.lint import Lint
from pre_commit_check.utilities import get_root
from pre_commit_check.git_status import GitStatusABC

REGION = "eu-central-1"


class GitRemoteUrlABC(ABC):

    @abstractmethod
    def get_remote_url(self) -> str:
        pass


class GitRemoteUrl(GitRemoteUrlABC):

    @cache
    def get_remote_url(self) -> str:
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


# @cache
# def get_remote_url() -> str:
#    """get git remote url"""
#    try:
#        return subprocess.run(["git", "config", "--get",
#                               "remote.origin.url"], check=True, encoding="utf-8",
#                              stdout=subprocess.PIPE).stdout.strip()
#    except subprocess.CalledProcessError as error:
#        print("git config --get remote.origin.url failed")
#        print("Is this really a git repository?")
#        print(error)
#        sys.exit(-1)


def is_aws_codecommit_repo(git_remote_url: GitRemoteUrlABC) -> bool:
    """Check if the local repo is a AWS CodeCommit repo."""
    remote_url = git_remote_url.get_remote_url()
    # url_git = f"git-codecommit.{REGION}.amazonaws.com/v1/repos"
    # url_http = f"codecommit::{REGION}://"
    if remote_url.startswith("codecommit::"):  # http cooler so first
        return True
    if remote_url.startswith("ssh://git-codecommit.") and ".amazonaws.com/v1/repos" in remote_url:  # ssh
        return True

    return False


def is_github_repo(git_remote_url: GitRemoteUrlABC) -> bool:
    """Check if the local repo is a GitHub repo."""
    # remote_url = git_remote_url.get_remote_url()
    return "@github.com:" in git_remote_url.get_remote_url()


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

        print(lines)
        return False
    except subprocess.CalledProcessError as error:
        print("git remote show origin failed")
        print("Is this really a git repository?")
        print(error)
        sys.exit(-1)


def check_default_branch_main_boto3(git_remote_url: GitRemoteUrlABC) -> None:
    """check if the default branch is main."""
    try:
        client = boto3.client('codecommit')
        remote_url = git_remote_url.get_remote_url()
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


@final
class GitWrapper:
    """Wrapper around GitPython and AWS CodeCommit."""

    def __init__(self):
        self.__repo = Repo(get_root())

    def get_origin_url(self) -> str:
        """the remote origin url."""
        return self.__repo.remotes.origin.url

    def get_head_sha(self) -> str:
        """the hexsha of the commit of the HEAD object."""
        return self.__repo.head.commit.hexsha

    def get_origin_head_sha(self) -> str:
        """ a remote tracking branch."""
        return self.__repo.refs['origin/main'].commit.hexsha

    def get_remote_origin_head_sha(self) -> str:
        """the remote head commit sha."""
        url = self.get_origin_url()
        ref = git.cmd.Git().ls_remote(url, heads=True)
        return ref.split('\t')[0]

    def get_nr_of_local_commits(self) -> int:
        """the list of local commits."""
        return len(list(self.__repo.iter_commits('origin/main..HEAD')))


@final
class CodeCommit(Lint):
    """Lint AWS CodeCommit and local git."""

    # git rev-parse origin/HEAD # to get the latest commit on the remote

    # git rev-parse HEAD          # to get the latest commit on the local

    # git config --get remote.origin.url

    # git ls-remote -h `git config --get remote.origin.url`

    def __init__(self):
        self.__git_wrapper = GitWrapper()

    def run(self, root: str, git_status: GitStatusABC) -> None:
        head_sha = self.__git_wrapper.get_head_sha()
        upstream_sha = self.__git_wrapper.get_origin_head_sha()
        if head_sha != upstream_sha:
            print(
                f"git: local commits {self.__git_wrapper.get_nr_of_local_commits()}")
        if self.__git_wrapper.get_remote_origin_head_sha() != upstream_sha:
            print("git: upstream changes")
