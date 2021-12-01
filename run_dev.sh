#!/bin/bash

# This script is recommended for running the docker container (in DEVELOPMENT mode).

# It can be executed without arguments.
#       bash run.sh

# Alternatively, default values can be overridden by passing their new values as follows:
#       DOCKER_IMAGE_TAG=v0.0.1 \
#       bash run.sh

# Additionally, an extra argument can be provided with a route to be mounted.
#   Example:
#       bash run_dev.sh ~/Documents/GitHub/ai/Notebooks

# pipefail is necessary to propagate exit codes (but it may not be supported by your shell)
set -o pipefail >/dev/null 2>&1

# Any subsequent(*) commands which fail will cause the shell script to exit immediately
set -ex

# start with an error if Docker isn't working...
docker version >/dev/null
printf "Docker version: %s\n" "$(docker version --format '{{.Server.Version}}')"

# >>>>>> Command line arguments >>>>>>
# Check if the first command line argument is empty
if
    [ -z "$1" ]
    echo "No additional volume provided."
then
    ADDITIONAL_VOLUME=""
else
    ADDITIONAL_VOLUME="--volume $1:/home/development/Notebooks"
    echo "Additional volume: " "${ADDITIONAL_VOLUME}"
fi
# >>>>>> Command line arguments >>>>>>

# >>>>>> Definitions >>>>>>
# general
CURRENT_DIR="$(pwd -P)"
# PARENT_DIR="$(dirname "$(pwd -P)")"
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
# volumes
#   shared directory
HOST_DIRPATH_TO_SHARED_FOLDER=${HOST_DIRPATH_TO_SHARED_FOLDER:-"${CURRENT_DIR}"}
CONTAINER_DIRPATH_TO_SHARED_FOLDER=${CONTAINER_DIRPATH_TO_SHARED_FOLDER:-'/home'}
CONTAINER_PARENT_DIRPATH_OF_SETUP_PY=${CONTAINER_PARENT_DIRPATH_OF_SETUP_PY:-'/home/'}
# <<<<<< Definitions <<<<<<

# >>>>>> Run the Docker container >>>>>>
#   ports
#       syntax: --publish HOST:CONTAINER
#   volumes
#       syntax: --volume HOST:CONTAINER
#
# For more info, run : docker run --help
#   --init: Makes process PID=1 be docker-init backed by tini: https://docs.docker.com/engine/reference/run/#specify-an-init-process
docker run --publish "${HOST_JUPYTER_NOTEBOOK_PORT}":"${CONTAINER_JUPYTER_NOTEBOOK_PORT}" \
    --volume "${HOST_DIRPATH_TO_SHARED_FOLDER}":"${CONTAINER_DIRPATH_TO_SHARED_FOLDER}" \
    ${ADDITIONAL_VOLUME} \
    --name "${DOCKER_CONTAINER_NAME}" \
    --detach \
    --init \
    --ipc="${DOCKER_CONTAINER_IPC_MODE}" \
    "${DOCKER_IMAGE_NAME}":"${DOCKER_IMAGE_TAG}"
# <<<<<< Run the Docker container <<<<<<

# >>>>>> Opt out from `vscode` experiments >>>>>>
# docker exec --tty --interactive "${DOCKER_CONTAINER_NAME}" bash -c 'mkdir -p /root/.vscode-server/data/Machine/ && printf "{\n\t\"python.defaultInterpreterPath\": \"/usr/bin/python3\",\n\t\"python.experiments.enabled\": false,\n\t\"jupyter.experiments.enabled\": false\n}\n" > /root/.vscode-server/data/Machine/settings.json && cat /root/.vscode-server/data/Machine/settings.json'
docker exec --tty --interactive "${DOCKER_CONTAINER_NAME}" bash -c 'mkdir -p /root/.vscode-server/data/Machine/ && printf "{\n\t\"python.experiments.enabled\": false,\n\t\"jupyter.experiments.enabled\": false\n}\n" > /root/.vscode-server/data/Machine/settings.json && cat /root/.vscode-server/data/Machine/settings.json'
# <<<<<< Opt out from `vscode` experiments <<<<<<

# >>>>>> Install `teselagen` library in "editable" mode in the container >>>>>>
docker exec "${DOCKER_CONTAINER_NAME}" bash -c "cd ${CONTAINER_PARENT_DIRPATH_OF_SETUP_PY}; python3 setup.py develop"
# <<<<<< Install `teselagen` library in "editable" mode in the container <<<<<<

# >>>>>> Run 'teselagen' Library Tests >>>>>>
# docker exec --tty --interactive --workdir="${CONTAINER_PARENT_DIRPATH_OF_SETUP_PY}" "${DOCKER_CONTAINER_NAME}" bash -c pytest --maxfail=100 --cov="teselagen" --cov-report term:skip-covered
# <<<<<< Run 'teselagen' Library Tests <<<<<<
