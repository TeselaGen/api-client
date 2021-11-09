#!/bin/bash

# We import values from the configuration file.
source ./config.sh

# For more info, run : docker run --help
#   --init: Makes process PID=1 be docker-init backed by tini: https://docs.docker.com/engine/reference/run/#specify-an-init-process
docker run --publish ${hostPort}:${containerPort} \
           --init \
           --name ${containerName} \
           --interactive \
           --tty \
           --detach \
           --ipc=host \
           ${imageName}:${versionTag}
