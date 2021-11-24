FROM ubuntu:18.04


# Fix DL4006 (https://deepsource.io/gh/The-Judge/docker_archlinux-php-fpm/issue/DOK-DL4006/description/)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]


# Enable the non interactive frontend for automatic installs, which accepts all default answers to questions.
ARG DEBIAN_FRONTEND=noninteractive


# Enable terminal colors
ENV TERM=xterm-color
ENV COLORTERM=truecolor


# Set the user as "root" during the building process
USER root
EXPOSE 8888


# >>>>>> Configure Locale >>>>>>
RUN set -ex \
    && apt-get update --fix-missing \
    # configure 'locale' properly
    && apt-get install -y locales \
    && locale-gen en_US.UTF-8 \
    \
    # uninstall non-essential libraries, so as not to increase the size of this layer (if applicable)
    \
    # ensure to remove package's state information after creating another layer in the docker image (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/*

# Set the locale environment variables after locale installation and configuration has been performed. Setting them before may show some unharmful warnings.
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV LC_CTYPE=UTF-8
# <<<<<< Configure Locale <<<<<<


# >>>>>> Install Python >>>>>>
RUN set -ex \
    && apt-get update \
    # configure Python3.9 repo on the system
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    # install Python3.9 (and pip3)
    python3.9 \
    python3-pip \
    # && python3.9 -m ensurepip --default-pip --user \
    # create symbolic links:
    #   python -> python3
    #   pip -> pip3
    && ln -sfn /usr/bin/python3.9 /usr/bin/python \
    && ln -sfn /usr/bin/python3.9 /usr/bin/python3 \
    && ln -s /usr/bin/pip3 /usr/bin/pip \
    # sanity checks
    && python --version \
    && python3 --version \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && apt-get update \
    && apt-get install -y \
    # --no-install-recommends \
    apt-utils \
    python3.9-distutils \
    # python3-setuptools \
    # python3 \
    # python3-pip \
    python3-venv \
    # install data transfer (and other) packages
    ca-certificates curl gnupg2 \
    # install packages required for building the docker image
    rsync \
    # install utility packages
    htop nano wget \
    # install OS dependencies for notebook server (https://github.com/jupyter/docker-stacks/blob/425794a0c2ffb0553a8c21e8eb97fbe94680c0ee/base-notebook/Dockerfile#L20-L35)
    bzip2 \
    sudo \
    locales \
    fonts-liberation \
    run-one \
    # sanity checks
    && pip --version \
    && pip3 --version \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN set -ex \
    # upgrade 'pip', 'setuptools', 'wheel'
    && python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    # && pip install --no-cache-dir --upgrade setuptools wheel \
    # sanity checks
    && python -m pip list | grep -iE '^pip|^setuptools|^wheel' \
    # Remove all items from the 'pip' cache
    && pip cache purge
# <<<<<< Install Python <<<<<<


# >>>>>> Install Git >>>>>>
RUN set -ex \
    && apt-get update \
    # Install Git
    && apt-get install -y git \
    # sanity checks
    && git --version \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# <<<<<< Install Git <<<<<<


# >>>>>> Install Poetry >>>>>>
# TODO: Starting from poetry 1.2, 'get-poetry.py' installer is deprecated. We should migrate to 'install-poetry.py'.
#       Also, check if the new script automatically configure the PATH (it seems no uses a 'POETRY_HOME' env variable).
# curl -sSL https://install.python-poetry.org
RUN set -ex \
    && apt-get update \
    && apt-get install -y \
    # install data transfer tool (and other required packages)
    ca-certificates curl gnupg2 \
    # download poetry installer
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -o get-poetry.py \
    # && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -o install-poetry.py \
    # install poetry
    && python3 get-poetry.py --version 1.1.10 \
    # && python3 install-poetry.py --version 1.2.0 \
    # remove unnecessary files
    && rm -rf get-poetry.py \
    # && rm -rf install-poetry.py \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/*

# Add poetry to the 'PATH' environment variable
ENV PATH="/root/.poetry/bin:$PATH"

# Set environment variable to tell poetry to install everything on system's python
ENV POETRY_VIRTUALENVS_CREATE=false

RUN set -ex \
    # sanity checks
    && poetry --version \
    # configurate poetry to install everything on system's python
    && poetry config virtualenvs.create false
# <<<<<< Install Poetry <<<<<<


# Set the current working directory
WORKDIR /tmp


# Copy files from the local folder to the working directory
COPY . .

# TODO: We should probably split the copy command more strategically.
#       We should decide which other files should be included in the '.dockerignore' file.
#       Otherwise meaningless file changes will invalidate the docker cache - hence, the build will be slower.
#           1. copy the 'poetry.lock' file (or create the requirements file using a poetry plugin)
#           2. install the requirements
#           3. copy the rest of the files
#       COPY poetry.lock .
#       COPY pyproject.toml .
#       COPY . .

# >>>>>> Install teselagen Library >>>>>>
RUN set -ex \
    # poetry installations are not editable # NOTE(diegovalenzuelaiturra: 2021-11-23): this may not be true anymore
    #
    # here we can update the `poetry.lock` file by running the `poetry update` command, then we can get the updated
    # file by copying it back to the shared folder, once the container is running. This could be done by running the
    # following command on the host.
    #   docker exec --tty --interactive tgclient bash -c 'mv -v /tmp/lib/poetry.lock /home/development/lib/poetry.lock'
    #
    && POETRY_VIRTUALENVS_CREATE=false poetry update \
    #
    # to avoid installing development packages, use 'poetry install --no-dev'
    && POETRY_VIRTUALENVS_CREATE=false poetry install \
    && cd .. \
    # sanity checks
    && python3 -c "import teselagen" \
    && python3 -c "import teselagen; print('teselagen version: ', teselagen.__version__)" \
    && poetry cache clear --all $(poetry cache list)
# >>>>>> Install teselagen Library >>>>>>


# >>>>>> Generate Jupyter Config >>>>>>
ENV PATH="~/.local/bin/jupyter-notebook:$PATH"

RUN set -ex \
    # sanity checks
    && jupyter --version \
    && jupyter notebook --version \
    # jupyter should have already been installed by the `poetry install` command
    && jupyter notebook --generate-config
# >>>>>> Generate Jupyter Config >>>>>>


# # >>>>>> Install Jupyter Extensions >>>>>>
# RUN set -ex \
#     && pip install jupyter_contrib_nbextensions \
#     && jupyter contrib nbextension install --system \
#     && jupyter nbextensions_configurator enable --user
# # <<<<<< Install Jupyter Extensions <<<<<<


# >>>>>> Clean Up >>>>>>
ARG PATH_TO_EXAMPLES=teselagen/examples/
ARG PATH_TO_EXAMPLES_REQUIREMENTS=teselagen/examples/requirements.txt

RUN set -ex \
    && mkdir -p /home/examples \
    # After the installation, we copy the examples folder to the home directory of the container.
    && rsync ${PATH_TO_EXAMPLES} /home/examples \
    --human-readable \
    --progress \
    --perms \
    --executability  \
    --recursive \
    --exclude "*requirements.txt"

# Then we delete the content of the working directory that was used for building and installing everything.
# Delete all from the local folder, except the file with the given name.
# RUN find . \! -name "*start.sh" -delete
# >>>>>> Clean Up >>>>>>


RUN set -ex \
    # set on bash start script
    && echo source "/tmp/on_bash_start.sh" >> ~/.bashrc \
    # provide proper permissions
    && chmod 775 /tmp/on_bash_start.sh \
    # log permissions
    && ls -lahG /tmp/on_bash_start.sh


# >>>>>> Entrypoint & Command >>>>>>
RUN set -ex \
    # provide proper permissions
    && chmod +x on_start.sh \
    # log permissions
    && ls -lahG /tmp/on_start.sh

# Set the default working directory for the container
WORKDIR /home/

ENTRYPOINT ["/tmp/on_start.sh"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]
# <<<<<< Entrypoint & Command <<<<<<
