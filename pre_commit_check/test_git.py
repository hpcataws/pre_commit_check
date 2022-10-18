"""tests for the git module"""

from pre_commit_check.git import (
    is_default_branch_main,
    GitRemoteUrlABC,
    GitRemoteUrl,
    is_github_repo
)

from pre_commit_check.test_decorators import skipIfGitHubAction

import os


class GitRemoteUrlMock(GitRemoteUrlABC):

    def __init__(self, url: str):
        self.__url = url

    def get_remote_url(self) -> str:
        return self.__url


@skipIfGitHubAction
def test_git_remote_url():
    """MVP test the git_remote_url function from the git module."""
    git = GitRemoteUrl()
    assert is_github_repo(git) is True


def test_is_github_repo():
    mock_false = GitRemoteUrlMock(
        "ssh://git-codecommit.eu-central-2.amazonaws.com/v1/repos/openmp-plus-x")
    mock_pre = GitRemoteUrlMock(
        "git@github.com:hpcataws/pre_commit_check.git")
    mock_rust = GitRemoteUrlMock(
        "git@github.com:tschuett/rust-stuff.git")

    assert is_github_repo(mock_false) is False
    assert is_github_repo(mock_pre) is True
    assert is_github_repo(mock_rust) is True


# FIXME: tox issues
# @skipIfGitHubAction
# def test_is_default_branch_main():
#    assert is_default_branch_main() is True


@skipIfGitHubAction
def test_decorator():
    print("test_decorator")
    if 'GITHUB_ACTIONS' not in os.environ:
        print("github action")
