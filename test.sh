#!/bin/sh

pytest
pytest --cov=pre_commit_check pre_commit_check

