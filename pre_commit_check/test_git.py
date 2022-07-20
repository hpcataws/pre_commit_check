"""tests for the git module"""

from pre_commit_check.git import get_remote_url, is_default_branch_main, is_aws_codecommit_repo, GitRemoteUrlABC, REGION

# is_github_repo


class GitRemoteUrlMock(GitRemoteUrlABC):

    def __init__(self, url: str):
        self.__url = url

    def get_remote_url(self) -> str:
        return self.__url


def test_git_remote_url():
    """MVP test the git_remote_url function from the git module."""
    get_remote_url()


# does not work with GitHub Actions
# def test_is_github_repo():
#    assert is_github_repo() is True


def test_is_default_branch_main():
    assert is_default_branch_main() is True


def test_is_aws_codecommit_repo():
    mock_false = GitRemoteUrlMock(
        "ssh://git-codecommit.eu-central-2.amazonaws.com/v1/repos/openmp-plus-x")
    mock_true = GitRemoteUrlMock(
        "ssh://git-codecommit.eu-central-1.amazonaws.com/v1/repos/openmp-plus-x")
    assert is_aws_codecommit_repo(mock_false) is False
    assert is_aws_codecommit_repo(mock_true) is True
