import pytest
import pre_commit_check.pre_commit_check


def test_git_remote_url():
    pre_commit_check.pre_commit_check.get_remote_url()


def test_is_github_repo():
    assert pre_commit_check.pre_commit_check.is_github_repo() == True


def test_is_default_branch_main():
    assert pre_commit_check.pre_commit_check.is_default_branch_main() == True
