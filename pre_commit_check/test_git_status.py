"""Mock class for testing print_short_status."""

from pre_commit_check.git_status import GitStatusABC


class GitStatusMock(GitStatusABC):
    """Mock class for GitStatus."""

    def __init__(self):
        self.__counter = 0

    def print_short_status(self, url: str) -> None:
        self.__counter += 1

    def get_counter(self) -> int:
        return self.__counter
