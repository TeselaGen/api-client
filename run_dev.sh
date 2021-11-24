#!/bin/bash

# This script is recommended for runing the docker container (in DEVELOPMENT mode).

# It can be executed without arguments.
#       sh run.sh

# Alternatively, default values can be overriden by passing their new values as follows:
#       DOCKER_IMAGE_TAG=v0.0.1 \
#       sh run.sh

# Additionally, an extra argument can be provided with a route to be mounted.
#   Example:
#       sh run_dev.sh ~/Documents/GitHub/ai/Notebooks


# pipefail is necessary to propagate exit codes
set -o pipefail

# Any subsequent(*) commands which fail will cause the shell script to exit immediately
set -e


# start with an error if Docker isn't working...
docker version > /dev/null


# >>>>>> Command line arguments >>>>>>
# Check if the first command line argument is empty
if [ -z "$1" ]
    echo "No additional volume provided."
then
      ADDITIONAL_VOLUME=""
else
      ADDITIONAL_VOLUME="--volume $1:/home/development/Notebooks"
      echo "Additional volume: " ${ADDITIONAL_VOLUME}
fi
# >>>>>> Command line arguments >>>>>>


# >>>>>> Definitions >>>>>>
# general
CURRENT_DIR="$(pwd -P)"
PARENT_DIR="$(dirname "$(pwd -P)")"
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
CONTAINER_DIRPATH_TO_SHARED_FOLDER=${CONTAINER_DIRPATH_TO_SHARED_FOLDER:-'/home/development/'}
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
           --volume ${HOST_DIRPATH_TO_SHARED_FOLDER}:${CONTAINER_DIRPATH_TO_SHARED_FOLDER} \
           ${ADDITIONAL_VOLUME} \
           --name ${DOCKER_CONTAINER_NAME} \
           --detach \
           --init \
           --ipc=${DOCKER_CONTAINER_IPC_MODE} \
           ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
# <<<<<< Run the Docker container <<<<<<


# >>>>>> Opt out from `vscode` experiments >>>>>>
# docker exec --tty --interactive "${DOCKER_CONTAINER_NAME}" bash -c 'mkdir -p /root/.vscode-server/data/Machine/ && printf "{\n\t\"python.defaultInterpreterPath\": \"/usr/bin/python3\",\n\t\"python.experiments.enabled\": false,\n\t\"jupyter.experiments.enabled\": false\n}\n" > /root/.vscode-server/data/Machine/settings.json && cat /root/.vscode-server/data/Machine/settings.json'
docker exec --tty --interactive "${DOCKER_CONTAINER_NAME}" bash -c 'mkdir -p /root/.vscode-server/data/Machine/ && printf "{\n\t\"python.experiments.enabled\": false,\n\t\"jupyter.experiments.enabled\": false\n}\n" > /root/.vscode-server/data/Machine/settings.json && cat /root/.vscode-server/data/Machine/settings.json'
# <<<<<< Opt out from `vscode` experiments <<<<<<


# >>>>>> Install `teselagen` library in "editable" mode in the container >>>>>>
docker exec "${DOCKER_CONTAINER_NAME}" bash -c "cd development; python3 setup.py develop"
# <<<<<< Install `teselagen` library in "editable" mode in the container <<<<<<