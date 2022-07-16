"""lints for bibtex files """

import os
import fileinput
import sys
from typing import final

import bibtexparser  # type: ignore

from pre_commit_check.lint import Lint
from pre_commit_check.fls_file import main_fls
from pre_commit_check.git import print_short_status


@final
class BibTeXLint(Lint):
    """Lint bib files and citations of main.tex """

    @staticmethod
    def get_citations() -> set[str]:
        """Return the bibtex entries cited by main.tex"""
        citations = set()
        with fileinput.input(files=("main.aux")) as file_input:
            for line in file_input:
                if line.startswith("\citation{"):
                    cites = line.removeprefix("\citation{").removesuffix("}\n")
                    split = cites.split(',')
                    for cite in split:
                        citations.add(cite)
        return citations

    # bib files are not input files for latex. they are inputs for bibtex
    @staticmethod
    def get_bib_files() -> set[str]:
        """Return the bib files needed by main.tex"""
        bib_files: set[str] = set()
        bbl_files: list[str] = []
        with main_fls() as fls_file:
            for line in fls_file:
                if line.endswith(".bbl"):
                    bbl_files.append(line.removeprefix("./"))

        if not bbl_files:
            return set()

        blg_files = map(lambda bbl: os.path.splitext(bbl)[
                        0]+'.blg', sorted(set(bbl_files)))
        with fileinput.input(files=list(blg_files)) as file_input:
            for line in file_input:
                if line.startswith("Database file"):
                    split = line.split(':')
                    file = line.removeprefix(
                        split[0]+": ").removesuffix("\n")
                    bib_files.add(file)
        return bib_files

    def check_bib_files(self) -> None:
        """Check the git status of the bib files of main.tex"""
        for bib_file in self.get_bib_files():
            print_short_status(bib_file)

    @staticmethod
    def check_citations() -> None:
        """Check for duplicate bib entries"""
        citations = BibTeXLint.get_citations()
        for bib_file in BibTeXLint.get_bib_files():
            with open(bib_file) as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
                for entry in bib_database.entries:
                    if not entry['ID'] in citations:
                        entry_id = entry['ID']
                        print(f"remove {entry_id:20} from {bib_file}")
                        sys.exit(-1)

    def run(self, root: str) -> None:
        if not os.path.exists("main.fls"):
            print("main.fls is missing")
            sys.exit(1)

        self.check_bib_files()
        BibTeXLint.check_citations()
