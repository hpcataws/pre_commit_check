import collections
from contextlib import contextmanager
import fileinput
from typing import final


@final
class MainFlsLines(collections.abc.Iterator):
    """line iterator over main.fls"""

    def __init__(self, file_descriptor):
        self.file_descriptor = file_descriptor

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            line = self.file_descriptor.readline()
            if not line:
                raise StopIteration
            if line.startswith("INPUT ") and not line.startswith("INPUT /usr/local"):
                return line.removeprefix("INPUT ").removesuffix("\n")


@contextmanager
def main_fls():
    """context manager for main.fls"""
    with open("main.fls", "r") as file_descriptor:
        try:
            yield MainFlsLines(file_descriptor)
        finally:
            pass
