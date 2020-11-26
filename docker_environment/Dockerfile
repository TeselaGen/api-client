# Ubuntu 18.04 (bionic)
# https://hub.docker.com/_/ubuntu/?tab=tags&name=bionic
# We use an updated ubuntu image.
ARG BASE_CONTAINER=ubuntu:bionic-20200112@sha256:bc025862c3e8ec4a8754ea4756e33da6c41cba38330d7e324abd25c8e0b93300

# We set the some default ARG values. Those values can be overwritten
# from the command line by using the "--build-arg" argument.


# Let's say we define default values for the "arg1" and "arg2"
# variables in the Dockerfile, as follows:
#   ARG arg1=old_value_1
#   ARG arg2=new_value_2
# And we want to update the values
#   "arg1" <- "new_value_1"
#   "arg2" <- "new_value_2",
# For this purpose, we can simply run
#         docker builder build . --build-arg arg1=new_value_1 --build-arg arg2=new_value_2
# This will overwrite the default values with the new values.


# (Default) IP address the notebook server will listen on.
ARG notebookIP=0.0.0.0

# (Default) The port the notebook server will listen on.
ARG notebookPort=8888

# We set the user as "root" during the building process
ARG USERNAME=root

FROM $BASE_CONTAINER AS base
USER $USERNAME
EXPOSE $notebookPort
ARG DEBIAN_FRONTEND=noninteractive

# We install needed dependencies
RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
    apt-utils \
    python3-setuptools\
    python3 \
    python3-pip \
    wget \
    nano \
    bzip2 \
    ca-certificates \
    sudo \
    locales \
    fonts-liberation \
    run-one \
    rsync && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create symbolic links:
#         python -> python3
#         pip -> pip3
RUN ln -sfn /usr/bin/python3.6 /usr/bin/python & \
    ln -s /usr/bin/pip3 /usr/bin/pip

# Upgrade pip
RUN pip install --upgrade pip

# We set the current working directory
WORKDIR /tmp

# We add/copy files from the local folder to the working directory
# NOTE : Using ADD allows to copy from remote sources (e.g, from a URL)
ADD . .

# We define some PATHs arguments
ARG PATH_TO_EXAMPLES=lib/teselagen/examples/
ARG PATH_TO_MODULE_REQUIREMENTS=lib/requirements.txt
ARG PATH_TO_EXAMPLES_REQUIREMENTS=lib/teselagen/examples/requirements.txt

# Install Library requirements
RUN python -m pip install  \
    --no-cache-dir  \
    --requirement=${PATH_TO_MODULE_REQUIREMENTS}

# Install Library
RUN cd lib/ && python setup.py install && cd ..

# Install requirements for the Examples
RUN python -m pip install \
    --no-cache-dir \
    --requirement=$PATH_TO_EXAMPLES_REQUIREMENTS

# Generate Jupyter Config
RUN jupyter notebook --generate-config

# Install Jupyter Extensions
RUN jupyter contrib nbextension install --system && \
    jupyter nbextensions_configurator enable --user

# After the installation, we copy the examples folder to the home directory
# And then we delete the content of the working directory that was used for
# building and installing everything.
RUN rsync ${PATH_TO_EXAMPLES} /home/ \
    --human-readable \
    --progress \
    --perms \
    --executability  \
    --recursive \
    --exclude "*requirements.txt"

# Delete all from the local folder, except the file with the given name.
#RUN find . \! -name "*start.sh" -delete

# Set on bash start script
RUN echo source "/tmp/on_bash_start.sh" >> ~/.bashrc
RUN chmod 775 /tmp/on_bash_start.sh

# Entry point
RUN chmod +x on_start.sh

# And we set the "home" as the default working directory
WORKDIR /home/
ENTRYPOINT ["/tmp/on_start.sh"]
