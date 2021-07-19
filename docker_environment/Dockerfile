# Ubuntu 18.04 (bionic)
# https://hub.docker.com/_/ubuntu/?tab=tags&name=bionic
# We use an updated ubuntu image.
ARG BASE_CONTAINER=ubuntu:bionic-20200112
# ARG BASE_CONTAINER=ubuntu:18.04

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
ENV LANG C.UTF-8
USER $USERNAME
EXPOSE $notebookPort
ARG DEBIAN_FRONTEND=noninteractive

# Configure Python3.9 repo on the system
RUN apt-get update && apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9 \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create symbolic links:
#         python -> python3
#         pip -> pip3
RUN ln -sfn /usr/bin/python3.9 /usr/bin/python & \
    ln -sfn /usr/bin/python3.9 /usr/bin/python3 & \
    ln -s /usr/bin/pip3 /usr/bin/pip

# We install needed dependencies
RUN apt-get update && \
    apt-get install -yq \
    #--no-install-recommends \
    apt-utils \
    python3.9-distutils \
    #python3-setuptools\
    #python3 \
    #python3-pip \
    python3-venv \
    wget \
    nano \
    bzip2 \
    ca-certificates \
    sudo \
    locales \
    fonts-liberation \
    run-one \
    htop \
    rsync && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Update pip
RUN python -m pip install --upgrade pip==21.1.3

# Install setuptools and wheel
RUN pip install setuptools==57.2.0 --no-cache-dir

# Install poetry
RUN set -x \
    && apt-get update \
    && apt-get install -y curl \
    && curl -sSL  https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -o get-poetry.py \
    && python3 get-poetry.py --version 1.1.7
    #&& rm -rf get-poetry.py
ENV PATH="/root/.poetry/bin:$PATH"

# Tell poetry to install everything on system's python
RUN poetry config virtualenvs.create false

# We set the current working directory
WORKDIR /tmp

# We add/copy files from the local folder to the working directory
# NOTE : Using ADD allows to copy from remote sources (e.g, from a URL)
COPY . .

# We define some PATHs arguments
ARG PATH_TO_EXAMPLES=lib/teselagen/examples/
ARG PATH_TO_MODULE_REQUIREMENTS=lib/requirements.txt
ARG PATH_TO_EXAMPLES_REQUIREMENTS=lib/teselagen/examples/requirements.txt

# Poetry installations are not editable
RUN cd lib/ && POETRY_VIRTUALENVS_CREATE=false poetry install && cd ..

# Generate Jupyter Config
ENV PATH="~/.local/bin/jupyter-notebook:$PATH"
RUN jupyter notebook --generate-config

# Install Jupyter Extensions
# RUN pip install jupyter_contrib_nbextensions && \
#     jupyter contrib nbextension install --system && \
#     jupyter nbextensions_configurator enable --user

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
#ENTRYPOINT ["tail", "-f", "/dev/null"]
