#!/bin/bash
# We import values from the configuration file.
source ./config.sh

# https://docs.docker.com/config/containers/container-networking/

# For more info, run : docker run --help
# --publish list : Publish a container's port(s) to the host
# --detach       : Run container in background and print container ID
docker run --publish ${hostPort}:${containerPort} \
           --name ${containerName} \
           --interactive \
           --tty \
           --detach \
           ${imageName}:${versionTag}
