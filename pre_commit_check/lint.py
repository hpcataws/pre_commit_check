"""the abstract base class for lints."""

from abc import ABC, abstractmethod

from pre_commit_check.git_status import GitStatusABC


class Lint(ABC):
    """Base class for lints."""

    @abstractmethod
    def run(self, root: str, git_status: GitStatusABC) -> None:
        """Abstract function for running lints."""
