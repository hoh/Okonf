#!/bin/bash

set -e

docker build -t okonf-test -f Dockerfile .
docker run okonf-test