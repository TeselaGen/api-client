#!/bin/bash

# This script is recommended for runing the docker container.

# It can be executed without arguments.
#       bash run.sh

# Alternatively, default values can be overriden by passing their new values as follows:
#       DOCKER_IMAGE_TAG=v0.0.1 \
#       bash run.sh


# pipefail is necessary to propagate exit codes (but it may not be supported by your shell)
bash | set -o pipefail > /dev/null 2>&1

# Any subsequent(*) commands which fail will cause the shell script to exit immediately
set -ex


# start with an error if Docker isn't working...
docker version > /dev/null
printf "Docker version: %s\n" "$(docker version --format '{{.Server.Version}}')"


# >>>>>> Definitions >>>>>>
DOCKER_IMAGE_NAME=${DOCKER_IMAGE_NAME:-'teselagen/python/tgclient'}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:-'v0.0.1'}
DOCKER_CONTAINER_NAME=${DOCKER_CONTAINER_NAME:-'tgclient'}
DOCKER_CONTAINER_IPC_MODE=${DOCKER_CONTAINER_IPC_MODE:-'host'}
HOST_JUPYTER_NOTEBOOK_PORT=${HOST_JUPYTER_NOTEBOOK_PORT:-'8888'}
CONTAINER_JUPYTER_NOTEBOOK_PORT=${CONTAINER_JUPYTER_NOTEBOOK_PORT:-'8888'}
# <<<<<< Definitions <<<<<<


# >>>>>> Run the Docker container >>>>>>
#   ports
#       sintax: --publish HOST:CONTAINER
#   volumes
#       sintax: --volume HOST:CONTAINER
#
# For more info, run : docker run --help
#   --init: Makes process PID=1 be docker-init backed by tini: https://docs.docker.com/engine/reference/run/#specify-an-init-process
docker run --publish ${HOST_JUPYTER_NOTEBOOK_PORT}:${CONTAINER_JUPYTER_NOTEBOOK_PORT} \
           --name ${DOCKER_CONTAINER_NAME} \
           --detach \
           --init \
           --ipc=${DOCKER_CONTAINER_IPC_MODE} \
           ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
# <<<<<< Run the Docker container <<<<<<
