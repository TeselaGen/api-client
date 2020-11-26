#!/bin/bash
# This script runs the docker environment in DEVELOPMENT mode
#
# It accepts a positional argument with a route to be mounted
#
# Ex:
#
# sh run_dev.sh ~/Documents/GitHub/ai/Notebooks

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
#
# We import values from the configuration file.
source ./config.sh
# https://docs.docker.com/config/containers/container-networking/
# For more info, run : docker run --help
# --publish list : Publish a container's port(s) to the host
# --detach       : Run container in background and print container ID

parentDir="$(dirname "$(pwd -P)")"
docker run --publish ${hostPort}:${containerPort} \
           --name ${containerName} \
           --volume $parentDir"/lib/:/home/development/lib" \
           $additionalVolume \
           --interactive \
           --tty \
           --detach \
           ${imageName}:${versionTag}
docker exec ${containerName} bash -c "cd development/lib; python3 setup.py develop"