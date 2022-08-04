"""context manager for reading .fls files."""

import collections
from contextlib import contextmanager
from typing import final

BLOCK_LIST = ["INPUT /usr/local", "INPUT /etc",
              "INPUT /usr/share", "INPUT /var/lib"]


def is_start_in_black_list(line: str) -> bool:
    """Check for black listed lines."""
    for entry in BLOCK_LIST:
        if line.startswith(entry):
            return True
    return False


@final
class MainFlsLines(collections.abc.Iterator):
    """line iterator over main.fls."""

    def __init__(self, file_descriptor):
        """Initialize the iterator."""
        self.file_descriptor = file_descriptor

    def __iter__(self):
        """Iterate function for abc.Iterator."""
        return self

    def __next__(self):
        """Next step method of the iterator."""
        while True:
            line = self.file_descriptor.readline()
            if not line:
                raise StopIteration
            if line.startswith("INPUT ") and not is_start_in_black_list(line):
                return line.removeprefix("INPUT ").removesuffix("\n")


@contextmanager
def main_fls():
    """Context manager for main.fls."""
    with open("main.fls", "r") as file_descriptor:
        try:
            yield MainFlsLines(file_descriptor)
        finally:
            pass
