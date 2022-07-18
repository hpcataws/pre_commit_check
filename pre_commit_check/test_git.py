from pre_commit_check.git import get_remote_url, is_default_branch_main, is_aws_codecommit_repo

# is_github_repo


def test_git_remote_url():
    get_remote_url()


# does not work with GitHub Actions
# def test_is_github_repo():
#    assert is_github_repo() is True


def test_is_default_branch_main():
    assert is_default_branch_main() is True


def test_is_aws_codecommit_repo():
    assert is_aws_codecommit_repo() is False
