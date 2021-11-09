#!/bin/bash

# This script is executed inside the docker, by the ENTRYPOINT inside the Dockerfile.

# Start Jupyter Notebook and set an empty token so no login is required
jupyter notebook --ip 0.0.0.0 \
                 --port 8888 \
                 --NotebookApp.allow_password_change=False \
                 --NotebookApp.token="" \
                 --notebook-dir="/home/" \
                 --allow-root \
                 --no-browser

# Necessary if no service is open by this script in the current screen
#/bin/bash
