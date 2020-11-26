#!/bin/bash

# NOTE:
#   I thought I could import values from a configuration
#   file adding the following line to this file:
#   source ./config.sh
#   But I'm not sure if it will work.
#   For now, it can't find the config.sh file.
#   And also, I'm not sure calling it from the ENTRYPOINT
#   will actually evaluate the values.

# This script is executed inside the docker,
# by the ENTRYPOINT inside the Dockerfile.

# Start Jupyter Notebook
# and set an empty token so no login is required
jupyter notebook --ip 0.0.0.0 \
                 --port 8888 \
                 --NotebookApp.allow_password_change=False \
                 --NotebookApp.token="" \
                 --notebook-dir="/home/" \
                 --allow-root \
                 --no-browser

# Necessary if no service is open by this script
# in the current screen
#/bin/bash