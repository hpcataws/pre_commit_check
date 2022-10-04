"""Local git commits."""

from typing import final

from pre_commit_check.git_status import GitStatusABC
from pre_commit_check.lint import Lint
from pre_commit_check.local_git import GitWrapper


@final
class LocalGit(Lint):
    """Lint local git."""

    # git rev-parse origin/HEAD # to get the latest commit on the remote

    # git rev-parse HEAD          # to get the latest commit on the local

    # git config --get remote.origin.url

    # git ls-remote -h `git config --get remote.origin.url`

    def __init__(self):
        """Run constructor."""
        self.__git_wrapper = GitWrapper()

    def run(self, root: str, git_status: GitStatusABC) -> None:
        """Run lint on local git."""
        head_sha = self.__git_wrapper.get_head_sha()
        upstream_sha = self.__git_wrapper.get_origin_head_sha()
        if head_sha != upstream_sha:
            print(
                f"git: local commits {self.__git_wrapper.get_nr_of_local_commits()}")
        if self.__git_wrapper.get_remote_origin_head_sha() != upstream_sha:
            print("git: upstream changes")
