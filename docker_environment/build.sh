#!/bin/bash
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
set -e

# This script builds the Docker image.
#         bash build.sh
#
# Use the flag "--clear" to delete intermediate images used as cache.
#         bash build.sh --clear
#

# We import values from the configuration file.
source ./config.sh

# We import the functions defined in utils.sh file
source ./utils.sh

# Remove (if copy exists) and then copy library into current folder
rm -rf ./lib
cp -avR ../lib ./lib

# We delete the image if it already exists.
delete_docker_image ${imageName} ${versionTag}

# We delete previous intermediate dangling images
# if the flag "--clear" has been passed from command line.
delete_intermediate_dangling_images $1

# --file           : Name of the Dockerfile (Default is 'PATH/Dockerfile')
# --tag            : Name and optionally a tag in the 'name:tag' format
# --squash         : Squash newly built layers into a single new layer
# --rm             : Remove intermediate containers after a successful
#                    build (default true)
# --force-rm       : Always remove intermediate containers
# --no-cache       : Do not use cache when building the image
# --build-arg list : Set build-time variables

# Example :
# To replace default ARG values,
#       docker builder build . \
#           --build-arg arg_name_1=new_value_1 \
#           --build-arg arg_name_2=new_value_new_value_2

# We build the image, and tag it with image name and version
echo "building ${imageName}:${versionTag}"

docker builder build . \
    --tag ${imageName}:${versionTag} \
    --squash \
    --force-rm \
    --rm \
    --no-cache \
#   --build-arg notebookPort=${notebookPort}

echo "built ${imageName}:${versionTag}"

# We delete posterior intermediate dangling images
# if the flag "--clear" has been passed from command line.
delete_intermediate_dangling_images $1

# Remove lib copy
rm -rf ./lib
