"""tests for the bibtex module."""

from pre_commit_check.bibtex import BibTeXLint
from pre_commit_check.test_utilities import mock_file

MAIN_AUX_CONTENT = """
\\citation{openmp51}
"""


def test_get_citations():
    """test the get_citations method from the bibtex module."""
    with mock_file("main.aux", MAIN_AUX_CONTENT):
        citations = BibTeXLint.get_citations()
        assert len(citations) == 1
