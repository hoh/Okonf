#!/usr/bin/env bash

set -e

pytest --cov=okonf --flakes okonf tests $@
coverage html

echo "Running Mypy"
mypy --ignore-missing-imports okonf

black --check okonf
