#!/bin/bash

# NOTE : If required, some of this values must be
#        manually included in the "on_start.sh" script

hostPort=8888
containerPort=8888

containerName=tgclient

imageName=teselagen/python/tgclient
versionTag=v0.0.1

# Not used yet -----> TODO: Update "on_start.sh"

# The IP address the notebook server will listen on.
# Default : "localhost"
notebookIP=0.0.0.0

# We set the port the notebook server will listen on.
# TODO : Check if this must be equal to the "containerPort"
notebookPort=8888
# notebookPort=containerPort

# We set an empty token, so the jupyter notebook
# does not requires a password.
notebookToken=""

# The directory to use for notebooks and kernels.
# We are starting in the /home/ directory which
# contains the "examples" folder.
notebookDirectory=/home/

# We don't allow to create a new password.
notebookAllowPasswordChange=False
