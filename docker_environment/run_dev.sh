#!/bin/bash
# This script runs the docker environment in DEVELOPMENT mode
# It accepts a positional argument with a route to be mounted

# Example:
#   sh run_dev.sh ~/Documents/GitHub/ai/Notebooks

# Any subsequent(*) commands which fail will cause the shell script to exit immediately
set -e

# Check argument is empty
if [ -z "$1" ]
then
      additionalVolume=""
else
      additionalVolume="--volume $1:/home/development/Notebooks"
      echo "Additional volume: " $additionalVolume
fi

# We import values from the configuration file.
source ./config.sh

parentDir="$(dirname "$(pwd -P)")"

# For more info, run: docker run --help
#   --init: Makes process PID=1 be docker-init backed by tini: https://docs.docker.com/engine/reference/run/#specify-an-init-process
docker run --publish ${hostPort}:${containerPort} \
           --volume $parentDir"/lib/:/home/development/lib" \
           $additionalVolume \
           --name ${containerName} \
           --detach \
           --init \
           --ipc=host \
           ${imageName}:${versionTag}

# Opt out from `vscode` experiments
# docker exec --tty --interactive ${containerName} bash -c 'mkdir -p /root/.vscode-server/data/Machine/ && printf "{\n\t\"python.defaultInterpreterPath\": \"/usr/bin/python3\",\n\t\"python.experiments.enabled\": false,\n\t\"jupyter.experiments.enabled\": false\n}\n" > /root/.vscode-server/data/Machine/settings.json && cat /root/.vscode-server/data/Machine/settings.json'
docker exec --tty --interactive ${containerName} bash -c 'mkdir -p /root/.vscode-server/data/Machine/ && printf "{\n\t\"python.experiments.enabled\": false,\n\t\"jupyter.experiments.enabled\": false\n}\n" > /root/.vscode-server/data/Machine/settings.json && cat /root/.vscode-server/data/Machine/settings.json'

# Install `teselagen` library in "editable" mode in the container
docker exec ${containerName} bash -c "cd development/lib; python3 setup.py develop"
