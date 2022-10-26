"""Mssing labels lint with BibTex."""

from typing import final
import fileinput
import re

from pre_commit_check.lint import Lint
from pre_commit_check.git_status import GitStatusABC


@final
class MissingLabelsLint(Lint):
    """Lint labels."""

    def run(self, root: str, git_status: GitStatusABC) -> None:
        """Find labels that were defined but not reference."""
        labels = set()
        mainlabels = set()
        with fileinput.input(files=("main.aux")) as file_input:
            for line in file_input:
                if line.startswith("\\newlabel{"):
                    first = line.removeprefix("\\newlabel{")
                    label = first.split('}')[0]
                    if label.startswith("fig.") or label.startswith("sec."):
                        labels.add(label)

        with fileinput.input(files=("main.tex")) as file_input:
            for line in file_input:
                idxs = [m.start() for m in re.finditer('figref', line)]
                for idx in idxs:
                    label = line[idx:-1].removeprefix("figref{")
                    label = label.split('}')[0]
                mainlabels.add(label)
                idxs = [m.start() for m in re.finditer('secref', line)]
                for idx in idxs:
                    label = line[idx:-1].removeprefix("secref{")
                    label = label.split('}')[0]
                    mainlabels.add(label)

        if labels-mainlabels:
            print(f"uncited label: {labels-mainlabels}")
