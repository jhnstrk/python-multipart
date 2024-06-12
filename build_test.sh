#!/bin/bash
set -eux -o pipefail

export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain


for PYTHON_VERSION in 3.8 3.9 3.10 3.11 3.12; do

  IMAGE_TAG=multipart-$PYTHON_VERSION
  docker build --tag $IMAGE_TAG \
    --build-arg PYTHON_VERSION=$PYTHON_VERSION \
    .

  docker run -it --rm $IMAGE_TAG \
    ruff format --check --diff multipart tests

  docker run -it --rm $IMAGE_TAG \
    ruff check multipart tests

  docker run -it --rm $IMAGE_TAG \
    inv mypy
    
  docker run -it --rm $IMAGE_TAG \
    inv test
done