#!/bin/bash

# This script is recommended for running the docker container.

# It can be executed without arguments.
#       bash run.sh

# Alternatively, default values can be overridden by passing their new values as follows:
#       DOCKER_IMAGE_TAG=v0.0.1 \
#       bash run.sh

set -o pipefail >/dev/null 2>&1 || true # bash specific option to propagate exit codes through pipes
set -o errexit                          # Exit immediately if a command exits with a non-zero status
set -o xtrace                           # Trace the execution of the script (debug mode)

# start with an error if Docker isn't working...
docker version >/dev/null
printf "[$(date)] Docker version: %s\n" "$(docker version --format '{{.Server.Version}}')"

# >>>>>> Definitions >>>>>>
# image
DOCKER_IMAGE_NAME=${DOCKER_IMAGE_NAME:-'teselagen/python/tgclient'}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:-'v0.0.1'}
# container
DOCKER_CONTAINER_NAME=${DOCKER_CONTAINER_NAME:-'tgclient'}
DOCKER_CONTAINER_IPC_MODE=${DOCKER_CONTAINER_IPC_MODE:-'host'}
# ports
#   jupyter notebook
HOST_JUPYTER_NOTEBOOK_PORT=${HOST_JUPYTER_NOTEBOOK_PORT:-'8888'}
CONTAINER_JUPYTER_NOTEBOOK_PORT=${CONTAINER_JUPYTER_NOTEBOOK_PORT:-'8888'}
# <<<<<< Definitions <<<<<<

# >>>>>> Run the Docker container >>>>>>
#   ports
#       syntax: --publish HOST:CONTAINER
#   volumes
#       syntax: --volume HOST:CONTAINER
#
# For more info, run : docker run --help
#   --init: Makes process PID=1 be docker-init backed by tini: https://docs.docker.com/engine/reference/run/#specify-an-init-process
echo "[$(date)] Running the Docker container ...: ${DOCKER_CONTAINER_NAME}"
docker run \
    --publish "${HOST_JUPYTER_NOTEBOOK_PORT}":"${CONTAINER_JUPYTER_NOTEBOOK_PORT}" \
    --name "${DOCKER_CONTAINER_NAME}" \
    --detach \
    --init \
    --ipc="${DOCKER_CONTAINER_IPC_MODE}" \
    "${DOCKER_IMAGE_NAME}":"${DOCKER_IMAGE_TAG}"
# <<<<<< Run the Docker container <<<<<<

echo "[$(date)] Done."
