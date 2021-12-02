#!/bin/bash

# This script is recommended for building the docker image.

# It can be executed without arguments.
#       bash build.sh

# Alternatively, default values can be overridden by passing their new values as follows:
#       DOCKER_IMAGE_TAG=v0.0.1 \
#       bash build.sh

# pipefail is necessary to propagate exit codes (but it may not be supported by your shell)
set -o pipefail >/dev/null 2>&1

# Any subsequent(*) commands which fail will cause the shell script to exit immediately
set -ex

# start with an error if Docker isn't working...
docker version >/dev/null
printf "Docker version: %s\n" "$(docker version --format '{{.Server.Version}}')"

# >>>>>> Definitions >>>>>>
DOCKER_IMAGE_NAME=${DOCKER_IMAGE_NAME:-teselagen/python/tgclient}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:-'v0.0.1'}
# <<<<<< Definitions <<<<<<add-apt-repository

# >>>>>> Remove old docker image >>>>>>
docker rmi -f "${DOCKER_IMAGE_NAME}":"${DOCKER_IMAGE_TAG}"
# <<<<<< Remove old docker image <<<<<<

# >>>>>> Build and tag the Docker image >>>>>>
#   Use the `--no-cache` flag of the `docker build` command if required.
#   Use the `--progress=plain` if you want to see the detaliled progress of the build
docker build --tag "${DOCKER_IMAGE_NAME}":"${DOCKER_IMAGE_TAG}" .
# <<<<<< Build and tag the Docker image <<<<<<
