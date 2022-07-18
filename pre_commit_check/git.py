"""utilities for working with git repositories"""

from functools import cache
import subprocess
import sys
from typing import final

import botocore      # type: ignore
import boto3         # type: ignore
from git import Repo
import git

from pre_commit_check.lint import Lint
from pre_commit_check.utilities import get_root

REGION = "eu-central-1"


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
    """check if the local repo is a GitHub repo."""
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

        print(lines)
        return False
    except subprocess.CalledProcessError as error:
        print("git remote show origin failed")
        print("Is this really a git repository?")
        print(error)
        sys.exit(-1)


def check_default_branch_main_boto3() -> None:
    """check if the default branch is main."""
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


@final
class GitWrapper:
    """Wrapper around GitPython and AWS CodeCommit."""

    def __init__(self):
        self.repo = Repo(get_root())

    def get_origin_url(self) -> str:
        """the remote origin url."""
        return self.repo.remotes.origin.url

    def get_head_sha(self) -> str:
        """the hexsha of the commit of the HEAD object."""
        return self.repo.head.commit.hexsha

    def get_origin_head_sha(self) -> str:
        """ a remote tracking branch."""
        return self.repo.refs['origin/main'].commit.hexsha

    def get_remote_origin_head_sha(self) -> str:
        """the remote head commit sha."""
        url = self.get_origin_url()
        ref = git.cmd.Git().ls_remote(url, heads=True)
        return ref.split('\t')[0]

    def get_nr_of_local_commits(self) -> int:
        """the list of local commits."""
        return len(list(self.repo.iter_commits('origin/main..HEAD')))


def print_short_status(url: str) -> None:
    """print short version of git status."""
    try:
        subprocess.run(["git", "status", "-s", url], check=True)
    except subprocess.CalledProcessError as error:
        print(f"git status failed {error}")


@final
class CodeCommit(Lint):
    """Lint AWS CodeCommit and local git."""

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
