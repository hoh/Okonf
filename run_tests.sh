#!/usr/bin/env bash

set -e

pytest --cov=okonf --flakes --pep8 okonf tests $@
coverage html

echo "Running Mypy"
mypy --ignore-missing-imports okonf
