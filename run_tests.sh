#!/usr/bin/env bash

set -e

pytest
coverage html

echo "Running Mypy"
mypy --ignore-missing-imports okonf

black --check okonf
