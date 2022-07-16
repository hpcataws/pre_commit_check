"""the abstract base class for lints"""

from abc import ABC, abstractmethod


class Lint(ABC):
    """Base class for lints"""

    @abstractmethod
    def run(self, root: str) -> None:
        """abstract function for running lints"""
