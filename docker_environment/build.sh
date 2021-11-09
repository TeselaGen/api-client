#!/bin/bash

# Any subsequent(*) commands which fail will cause the shell script to exit immediately
set -e

# This scripts is recommended to be used for building the docker image.

# You can simply execute it by calling the script without arguments.
#       sh build.sh

# Use the flag "--clear" to delete intermediate images used as cache.
#         bash build.sh --clear

# We import values from the configuration file.
source ./config.sh

# We import the functions defined in utils.sh file
source ./utils.sh

# Remove (if copy exists) and then copy library into current folder
rm -rf ./lib
cp -avR ../lib ./lib

# We delete the image if it already exists.
delete_docker_image ${imageName} ${versionTag}

# We delete previous intermediate dangling images if the flag "--clear" has been passed from command line.
delete_intermediate_dangling_images $1

# We build the image, and tag it with image name and version
# Use the `--no-cache` flag of the `docker build` command if required.
echo "building ${imageName}:${versionTag}"
docker build --no-cache --tag ${imageName}:${versionTag} .
echo "built ${imageName}:${versionTag}"

# We delete posterior intermediate dangling images if the flag "--clear" has been passed from command line.
delete_intermediate_dangling_images $1

# Remove lib copy
rm -rf ./lib
