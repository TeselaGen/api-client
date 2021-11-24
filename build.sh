#!/bin/bash

# This script is recommended for building the docker image.

# It can be executed without arguments.
#       sh build.sh

# Alternatively, default values can be overriden by passing their new values as follows:
#       DOCKER_IMAGE_TAG=v0.0.1 \
#       sh build.sh


# pipefail is necessary to propagate exit codes
set -o pipefail

# Any subsequent(*) commands which fail will cause the shell script to exit immediately
set -ex


# start with an error if Docker isn't working...
docker version > /dev/null


# >>>>>> Definitions >>>>>>
DOCKER_IMAGE_NAME=${DOCKER_IMAGE_NAME:-teselagen/python/tgclient}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:-'v0.0.1'}
# <<<<<< Definitions <<<<<<


# >>>>>> Remove old docker image >>>>>>
docker rmi -f ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
# <<<<<< Remove old docker image <<<<<<


# >>>>>> Build and tag the Docker image >>>>>>
#   Use the `--no-cache` flag of the `docker build` command if required.
docker build --tag ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} .
# <<<<<< Build and tag the Docker image <<<<<<