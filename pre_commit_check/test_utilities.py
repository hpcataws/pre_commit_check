"""utilities for testing."""

from contextlib import contextmanager
import os


@contextmanager
def mock_file(name: str, content: str):
    with open(name, 'w') as file_descriptor:
        file_descriptor.write(content)
    try:
        yield
    finally:
        os.remove(name)


# @contextlib.contextmanager
# def log_time_in_scope(action_name):
#    log_time('start', action_name)
#    t_start = time.time()
#    try:
#        yield
#    finally:
#        log_time('end', action_name, time.time() - t_start)
