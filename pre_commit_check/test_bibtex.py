"""tests for the bibtex module."""

from pre_commit_check.bibtex import BibTeXLint
from pre_commit_check.test_utilities import mock_file
from pre_commit_check.utilities import get_root
from pre_commit_check.test_git_status import GitStatusMock

MAIN_AUX_CONTENT = """
\\citation{openmp51}
"""

MAIN_FLS_CONTENT = """
INPUT ./main.bbl
"""

MAIN_BLG_CONTENT = """
Database file #1: main.bib
"""

MAIN_BIB_CONTENT = """
@manual{openmp51,
    author = "{OpenMP Forum}",
    title  = "OpenMP 5.1 Specification",
    url    = "https://www.openmp.org/wp-content/uploads/OpenMP-API-Specification-5-1.pdf",
    year   = 2020,
    month  = "nov"
}
"""


def test_get_citations():
    """test the get_citations method from the bibtex module."""
    with mock_file("main.aux", MAIN_AUX_CONTENT):
        citations = BibTeXLint.get_citations()
        assert len(citations) == 1


def test_get_bib_files():
    """ test the get_bib_files method from the bibtex module."""
    with mock_file("main.fls", MAIN_FLS_CONTENT):
        with mock_file("main.blg", MAIN_BLG_CONTENT):
            bib_files = BibTeXLint.get_bib_files()
            print(bib_files)
            assert len(bib_files) == 1


def test_check_bib_files():
    git_status_mock = GitStatusMock()
    root = get_root()
    with mock_file("main.aux", MAIN_AUX_CONTENT):
        with mock_file("main.fls", MAIN_FLS_CONTENT):
            with mock_file("main.blg", MAIN_BLG_CONTENT):
                with mock_file("main.bib", MAIN_BIB_CONTENT):
                    bib_tex_lint = BibTeXLint()
                    bib_tex_lint.run(root, git_status_mock)

    assert git_status_mock.get_counter() == 1
