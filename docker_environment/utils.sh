#!/bin/bash

# docker images --quiet flag : Only show numeric IDs

# We define a function to delete intermediate dangling images.
function delete_intermediate_dangling_images(){
    if [[ $1 == "--clear" ]]; then
        intermediateImagesIDs=$(docker images --filter "dangling=true" --quiet)
        if [[ $intermediateImagesIDs ]]; then
            echo "cleaning the following dangling intermediate images"
            docker rmi --force $(docker images --filter "dangling=true" --quiet)
            # NOTE : We are not using the following command, because we should first verify
            #        it will not delete images that are being used for running containers.
            #        docker rmi $(docker images -a | grep none | awk '{print $3}') --force
            echo "cleaned dangling intermediate images"
        else
            echo "no intermediate images were found"
        fi
    fi
}


# We define a function to delete a docker image.
function delete_docker_image(){
    # Recieves imageName and versionTag as arguments
    imageName=$1
    versionTag=$2
    foundImageIDs=$(docker images ${imageName}:${versionTag} --quiet)
    # Delete the image if it exists.
    if [[ $foundImageIDs ]]; then
        echo "Removing existent images"
        # docker rmi --force $(docker images ${imageName}:${versionTag} --quiet)
        docker rmi --force ${imageName}:${versionTag}
    else
        echo "No previous images were found."
    fi
}
