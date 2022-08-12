#!/bin/bash

set -e

mkdir -p "htmlcov"

docker build -t okonf-test -f Dockerfile .
docker run --rm -ti \
  --mount type=bind,readonly,source="$(pwd)"/okonf,target=/opt/okonf \
  --mount type=bind,readonly,source="$(pwd)"/tests,target=/opt/tests \
  --mount type=bind,source="$(pwd)"/htmlcov,target=/opt/htmlcov \
    okonf-test $@
