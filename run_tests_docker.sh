#!/usr/bin/env bash

set -e

mkdir -p "htmlcov"

podman build -t okonf-test -f Dockerfile .
podman run --rm -ti \
  --mount type=bind,readonly,source="$(pwd)"/okonf,target=/opt/okonf/okonf \
  --mount type=bind,readonly,source="$(pwd)"/tests,target=/opt/okonf/tests \
  --mount type=bind,source="$(pwd)"/htmlcov,target=/opt/okonf/htmlcov \
    okonf-test $@
