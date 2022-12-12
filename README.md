![python-package-conda](https://github.com/hpcataws/pre_commit_check/actions/workflows/python-package-conda.yml/badge.svg)

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/hpcataws/pre_commit_check/badge)](https://api.securityscorecards.dev/projects/github.com/hpcataws/pre_commit_check)

# pre_commit_check

```console
> python -m build
> pip install -r requirements.txt
```

* Python >= 3.10

# Development mode

```console
> pip install --editable .
```

```console
> /Users/king/opt/anaconda3/bin/precommitcheck
```

# Test

```console
> pytest
> pytest --html=report.html --self-contained-html
```

```console
> tox
```

* Static analyzers

```console
> ./check.sh
```

# TODO

* structural pattern matching
