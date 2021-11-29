#!/bin/bash

# This script is executed inside the docker, by the ENTRYPOINT inside the Dockerfile.

# It can be executed without arguments
#       bash on_start.sh

# Alternatively, default values can be overridden by passing their new values as follows:
#       JUPYTER_NOTEBOOK_PORT=8888 \
#       bash on_start.sh

# # NOTE: We disable strict mode because we don't want to fail the container if the script fails.
# # pipefail is necessary to propagate exit codes (but it may not be supported by your shell)
# # bash | set -o pipefail > /dev/null 2>&1
# #
# # Any subsequent(*) commands which fail will cause the shell script to exit immediately
# # set -ex
# #
# # start with an error if jupyter isn't working...
# # jupyter --version > /dev/null

# >>>>>> Definitions >>>>>>
JUPYTER_NOTEBOOK_IP=${JUPYTER_NOTEBOOK_IP:-'0.0.0.0'}
JUPYTER_NOTEBOOK_PORT=${JUPYTER_NOTEBOOK_PORT:-'8888'}
JUPYTER_NOTEBOOK_DIR=${JUPYTER_NOTEBOOK_DIR:-'/home/'}
# <<<<<< Definitions <<<<<<

# >>>>>> Start Jupyter Notebook >>>>>>
# Start Jupyter Notebook and set an empty token so no login is required
jupyter notebook --ip ${JUPYTER_NOTEBOOK_IP} \
    --port ${JUPYTER_NOTEBOOK_PORT} \
    --NotebookApp.allow_password_change=False \
    --NotebookApp.token='' \
    --notebook-dir=${JUPYTER_NOTEBOOK_DIR} \
    --allow-root
#  --no-browser
# <<<<<< Start Jupyter Notebook <<<<<<

# Necessary if no service is open by this script in the current screen
#/bin/bash
