

from pre_commit_check.latex import LaTexLint
from pre_commit_check.test_git_status import GitStatusMock
from pre_commit_check.test_utilities import mock_file

# this is fake!
MAIN_FLS_CONTENT = """
INPUT ./main.some
"""

# this is fake!
MAIN_SOME_CONTENT = """
touch
"""


def test_check_input_files():
    status = GitStatusMock()
    with mock_file("main.fls", MAIN_FLS_CONTENT):
        with mock_file("main.some", MAIN_SOME_CONTENT):
            LaTexLint.check_input_files(status)
    assert status.get_counter() == 1
