#import pytest
from pre_commit_check.git import get_remote_url, is_github_repo, is_default_branch_main


def test_git_remote_url():
    get_remote_url()


def test_is_github_repo():
    assert is_github_repo() is True


def test_is_default_branch_main():
    assert is_default_branch_main() is True
