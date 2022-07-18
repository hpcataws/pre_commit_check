"""tests for the bibtex module."""

from pre_commit_check.bibtex import BibTeXLint
from pre_commit_check.test_utilities import mock_file

MAIN_AUX_CONTENT = """
\\citation{openmp51}
"""

MAIN_FLS_CONTENT = """
INPUT ./main.bbl
"""

MAIN_BLG_CONTENT = """
Database file #1: main.bib
"""


def test_get_citations():
    """test the get_citations method from the bibtex module."""
    with mock_file("main.aux", MAIN_AUX_CONTENT):
        citations = BibTeXLint.get_citations()
        assert len(citations) == 1


def test_get_bib_files():
    with mock_file("main.fls", MAIN_FLS_CONTENT):
        with mock_file("main.blg", MAIN_BLG_CONTENT):
            bib_files = BibTeXLint.get_bib_files()
            print(bib_files)
            assert len(bib_files) == 1
