#!/bin/bash

# If both, container and image, already exist.
# This script will attempt to remove them, and
# then it will build the image and run the
# container.

# We import values from the configuration file.
source ./config.sh

containterID=$(docker ps --filter="name=${containerName}" --all --quiet)
imageID=$(docker images $imageName:$versionTag --all --quiet)

# Remove existent container.
if [[ ${containterID} ]]; then
    echo "Removing existent container : "
    echo "Name : ${containerName} "
    echo "ID   : ${containerID} "

    docker rm --force ${containerName}

    echo "Existent container was removed"
else
    echo "No existent container was found"
fi

# Remove existent image.
if [[ ${imageID} ]]; then
    echo "Removing existent image : "
    echo "Name : ${imageName} "
    echo "ID   : ${imageID} "

    docker rmi --force ${imageName}:${versionTag}

    echo "Existent image was removed"
else
    echo "No existent image was found"
fi

# Build image.
echo "Runing : build.sh --clear"
bash build.sh --clear

# Run container.
echo "Runing : run.sh"
bash run.sh
