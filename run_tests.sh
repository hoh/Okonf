#!/usr/bin/env bash

set -e

pytest -m "not slow"
coverage html

echo "Running Mypy"
mypy --ignore-missing-imports okonf

black --check okonf
