#!/bin/bash

# This script is recommended for building the docker image.

# It can be executed without arguments.
#       bash build.sh

# Alternatively, default values can be overridden by passing their new values as follows:
#       DOCKER_IMAGE_TAG=v0.0.1 \
#       bash build.sh

set -o pipefail >/dev/null 2>&1 || true # bash specific option to propagate exit codes through pipes
set -o errexit                          # Exit immediately if a command exits with a non-zero status
set -o xtrace                           # Trace the execution of the script (debug mode)

# if [ "$1" == "--dev" ]; then
#     set -o xtrace                       # Trace the execution of the script (debug mode)
# fi

# start with an error if Docker isn't working...
docker version >/dev/null
printf "[$(date)] Docker version: %s\n" "$(docker version --format '{{.Server.Version}}')"

# >>>>>> Definitions >>>>>>
DOCKER_IMAGE_NAME=${DOCKER_IMAGE_NAME:-teselagen/python/tgclient}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:-'v0.0.1'}
# <<<<<< Definitions <<<<<<

# >>>>>> Remove old docker image >>>>>>
echo "[$(date)] Removing the Docker image ...: ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
docker rmi --force "${DOCKER_IMAGE_NAME}":"${DOCKER_IMAGE_TAG}"
# <<<<<< Remove old docker image <<<<<<

# >>>>>> Build and tag the Docker image >>>>>>
if [ "$1" == "--dev" ]; then
    echo "[$(date)] Building the Docker image (without cache) ...: ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
    docker build --no-cache --progress=plain -t "${DOCKER_IMAGE_NAME}":"${DOCKER_IMAGE_TAG}" .
else
    echo "[$(date)] Building the Docker image ...: ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
    docker build --tag "${DOCKER_IMAGE_NAME}":"${DOCKER_IMAGE_TAG}" .
fi
# <<<<<< Build and tag the Docker image <<<<<<

echo "[$(date)] Done."
