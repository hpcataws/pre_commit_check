"""decorators for pytests"""

from collections.abc import Callable
import platform
import os


def skipIfDarwin(func: Callable[[], None]) -> Callable[[], None]:
    """Skip this test if it is running on Darwin."""
    def wrapper() -> None:
        if platform.system() != 'Darwin':
            func()
    return wrapper


def skipIfLinux(func: Callable[[], None]) -> Callable[[], None]:
    """Skip this test if it is running on Linux."""
    def wrapper() -> None:
        if platform.system() != 'Linux':
            func()
    return wrapper


def skipIfWindows(func: Callable[[], None]) -> Callable[[], None]:
    """Skip this test if it is running on Windows."""
    def wrapper() -> None:
        if platform.system() != 'Windows':
            func()
    return wrapper


def skipIfGitHubAction(func: Callable[[], None]) -> Callable[[], None]:
    """Skip this test if it is running on a GitHub Action."""
    def wrapper() -> None:
        if 'GITHUB_ACTIONS' not in os.environ:
            func()
    return wrapper
