#!/bin/bash

set -e

docker build -t okonf-test -f Dockerfile .
docker run --rm --mount type=bind,source="$(pwd)"/htmlcov,target=/opt/htmlcov \
    okonf-test /opt/run_tests.sh $@
