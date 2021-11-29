
# Docker environment for API

## Build and Run

Here are some guidelines to _build_ and _run_ the docker container for the `TeselaGen Python Client`.

1. Build the docker image from the `Dockerfile`

    ```bash
    sh build.sh
    ```

1. Run the docker container from the (already built) docker image

    ```bash
    sh run.sh
    ```

1. Alternatively, build the docker image and run the docker container in one line.

    ```bash
    sh build.sh && sh run.sh
    ```

1. Once the docker container is running, you can access jupyter notebooks from your browser at `localhost:8888`

1. You can create your own run command to mount folders from your computer into the container. Alternatively, you may  use the `sh run_dev.sh <path/to/local/folder>` command (instead of `run.sh`) to mount a directory into `/home/development/Notebooks`.

# Others

Here we list some common commands.

1. To list _runing_ containers

    ```bash
    docker ps
    ```

    Use the `--all` flag to list _all_ containers

    ```bash
    docker ps --all
    ```

1. To list all _images_

    ```bash
    docker images --all
    ```

1. Restart the container

    Replace `containerName`

    ```bash
    docker restart containerName
    ```

1. Stop the running container

    Replace `containerName`

    ```bash
    docker stop containerName
    ```

1. Start the container

    Replace `containerName`

    ```bash
    docker start containerName
    ```

1. Remove the container

    Replace `containerName`

    Use the `--force` flag to force the removal of a running container.

    ```bash
    docker rm containerName --force
    ```

1. Remove the image

    Replace `imageName` and `versionTag`

    Use the flag `--force` to force the removal of the image.

    ```bash
    docker rmi imageName:$versionTag --force
    ```

1. To pretty print the list of containers using a `Go` template

    ```bash
    docker ps --all --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}\t{{.ID}}\t{{.Mounts}}' --no-trunc
    ```

1. Open a terminal from inside the container

    Replace `containerName`

    ```bash
    docker exec --tty --interactive containerName bash
    ```

1. Verify the library is installed

    * From inside the container

        ```bash
        pip freeze | grep --ignore-case teselagen
        ```

    * From outside the container

        ```bash
        docker exec --tty --interactive tgclient  bash -c "pip freeze | grep --ignore-case teselagen"
        ```

1. Get the token of the `Jupyter Notebook` that runs inside the container

    Replace `containerName`

    Calling `bash` with the `-c` option allows to append a string with the specific commands that are going to be run directly inside the container.

    Here is an example to run the command `jupyter notebook list` inside the container, to get the notebook token.

    ```bash
    docker exec --tty --interactive containerName bash -c "jupyter notebook list"
    ```
