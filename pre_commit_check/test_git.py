"""tests for the git module"""

from pre_commit_check.git import is_default_branch_main, is_aws_codecommit_repo, GitRemoteUrlABC, is_github_repo


class GitRemoteUrlMock(GitRemoteUrlABC):

    def __init__(self, url: str):
        self.__url = url

    def get_remote_url(self) -> str:
        return self.__url


# def test_git_remote_url():
#    """MVP test the git_remote_url function from the git module."""
#    get_remote_url()


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


def test_is_default_branch_main():
    assert is_default_branch_main() is True


def test_is_aws_codecommit_repo():
    mock_openmp = GitRemoteUrlMock(
        "ssh://git-codecommit.eu-central-1.amazonaws.com/v1/repos/openmp-plus-x")
    mock_bench = GitRemoteUrlMock(
        "ssh://git-codecommit.eu-central-1.amazonaws.com/v1/repos/benchmark-learning")
    mock_other_region = GitRemoteUrlMock(
        "ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/BerlinTM")
    mock_http = GitRemoteUrlMock(
        "codecommit::eu-central-1://benchmark-learning")
    assert is_aws_codecommit_repo(mock_openmp) is True
    assert is_aws_codecommit_repo(mock_bench) is True
    assert is_aws_codecommit_repo(mock_other_region) is True
    assert is_aws_codecommit_repo(mock_http) is True


# FIXME: failure
