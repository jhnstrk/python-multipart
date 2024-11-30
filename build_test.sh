#!/bin/bash
set -eux -o pipefail

export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain


for PYTHON_VERSION in 3.8 3.9 3.10 3.11 3.12; do

  IMAGE_TAG=multipart-$PYTHON_VERSION
  docker build --tag $IMAGE_TAG \
    --build-arg PYTHON_VERSION=$PYTHON_VERSION \
    .

  # Run linters
  docker run -it --rm $IMAGE_TAG \
    scripts/check

  # Run tests
  docker run -it --rm $IMAGE_TAG \
    scripts/test

  # Run rename test
  docker run -it --rm $IMAGE_TAG \
    scripts/rename

done