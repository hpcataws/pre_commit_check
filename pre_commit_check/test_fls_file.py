
from pre_commit_check.fls_file import main_fls
from pre_commit_check.test_utilities import mock_file

MAIN_FLS_CONTENT = """
hi
"""


def test_main_fls():
    with mock_file("main.fls", MAIN_FLS_CONTENT):
        with main_fls() as fls_file:
            for line in fls_file:
                assert line.endswith("hi")
