FROM ubuntu:18.04

# Fix DL4006 (https://deepsource.io/gh/The-Judge/docker_archlinux-php-fpm/issue/DOK-DL4006/description/)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Enable the non interactive frontend for automatic installs, which accepts all default answers to questions.
ARG DEBIAN_FRONTEND=noninteractive

# Enable terminal colors
ENV TERM=xterm-color \
    COLORTERM=truecolor

# Set the user as "root" during the building process
USER root
EXPOSE 8888

# >>>>>> Configure Locale >>>>>>
RUN set -ex && \
    # fixes error "unable to initialize frontend: Dialog"
    # https://github.com/moby/moby/issues/27988#issuecomment-462809153
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get update -y --no-allow-insecure-repositories && \
    apt-get install -y --no-install-recommends \
    locales \
    && \
    # configure 'locale' properly
    locale-gen en_US.UTF-8 && \
    \
    # uninstall non-essential libraries, so as not to increase the size of this layer (if applicable)
    \
    # ensure to remove package's state information after creating another layer in the docker image (it can be recreated with 'apt-get update')
    rm -rf /var/lib/apt/lists/*

# Set the locale environment variables after locale installation and configuration has been performed. Setting them before may show some unharmful warnings.
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=UTF-8
# <<<<<< Configure Locale <<<<<<

# >>>>>> Install Python >>>>>>
RUN set -ex && \
    apt-get update -y --no-allow-insecure-repositories && \
    # configure Python3.9 repo on the system
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    rm -rf /var/lib/apt/lists/*

# NOTE: 'python*-venv' is required by poetry (since it installation script requires 'ensurepip', which is
#       currently not provided by the deadsnakes ppa). See https://github.com/deadsnakes/issues/issues/148
RUN set -ex && \
    apt-get update -y --no-allow-insecure-repositories && \
    apt-get install -y --no-install-recommends \
    # install Python3.9 (and pip3)
    # python3.9 python3-pip \
    python3.9 python3.9-dev python3.9-venv \
    && \
    python3.9 -m ensurepip --default-pip && \
    python3.9 -m pip install --upgrade pip && \
    #
    # python3.9 -m ensurepip --default-pip --user && \
    # python3.9 -m pip install --upgrade pip --user && \
    # export PATH="/root/.local/bin:$PATH" && \
    #
    # create symbolic links:
    #   python -> python3
    #   pip -> pip3
    ln -sfn /usr/bin/python3.9 /usr/bin/python && \
    ln -sfn /usr/bin/python3.9 /usr/bin/python3 && \
    ln -s /usr/bin/pip3 /usr/bin/pip && \
    # sanity checks
    python --version && \
    python3 --version && \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    rm -rf /var/lib/apt/lists/*

# Add 'pip' to the 'PATH' environment variable
ENV PATH="/root/.local/bin:$PATH"

RUN set -ex && \
    apt-get update -y --no-allow-insecure-repositories && \
    apt-get install -y --no-install-recommends \
    apt-utils \
    python3.9-distutils \
    # python3-setuptools \
    # python3 \
    # python3-pip \
    # python3-venv \
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
    run-one && \
    # sanity checks
    pip --version && \
    pip3 --version && \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN set -ex && \
    # print installed versions (pip==21.3.1 and setuptools==58.1.0 and wheel is not installed)
    python -m pip list | grep -iE '^pip|^setuptools|^wheel' && \
    # upgrade 'pip', do not upgrade 'setuptools', and install 'wheel' | pip>=21.3.1 setuptools==58.1.0 wheel>=0.37.0 |
    python -m pip install --no-cache-dir --upgrade pip>=21.3.1 setuptools==58.1.0 wheel>=0.37.0 && \
    # sanity checks
    python -m pip list | grep -iE '^pip|^setuptools|^wheel' && \
    # Remove all items from the 'pip' cache
    pip cache purge
# <<<<<< Install Python <<<<<<

# >>>>>> Install Git >>>>>>
RUN set -ex && \
    apt-get update -y --no-allow-insecure-repositories && \
    apt-get install -y --no-install-recommends \
    # install data transfer tool (and other required packages)
    ca-certificates curl gnupg2 && \
    # Install Git
    apt-get install -y git && \
    # sanity checks
    git --version && \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    rm -rf /var/lib/apt/lists/*
# <<<<<< Install Git <<<<<<

# >>>>>> Install Poetry >>>>>>
# NOTE: https://github.com/tiangolo/poetry-version-plugin/tree/0.1.3#install-poetry-120a1
#
# TODO: Starting from poetry 1.2, 'get-poetry.py' installer is deprecated. We should migrate to 'install-poetry.py'.
#       Also, check if the new script automatically configure the PATH (it seems no uses a 'POETRY_HOME' env variable).
#           curl -sSL https://install.python-poetry.org
RUN set -ex && \
    apt-get update -y --no-allow-insecure-repositories && \
    apt-get install -y --no-install-recommends \
    # install data transfer tool (and other required packages)
    ca-certificates curl gnupg2 && \
    #
    # download poetry installer (1.1.10)
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -o get-poetry.py && \
    # install poetry (1.1.10)
    python3 get-poetry.py --version 1.1.10 && \
    # remove unnecessary files (1.1.10)
    rm -rf get-poetry.py && \
    #
    #       # download poetry installer (1.2.0a2)
    #       curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -o install-poetry.py && \
    #       # install poetry (1.2.0a2)
    #       # python install-poetry.py --version 1.2.0a2 && \
    #       python install-poetry.py --preview && \
    #       # remove unnecessary files (1.2.0a2)
    #       rm -rf install-poetry.py && \
    #       # # export PATH="/root/.local/bin:$PATH" && \
    #
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    rm -rf /var/lib/apt/lists/*

# NOTE: automatically set to to $HOME/.poetry/bin by the installer, by modifying the profile file at $HOME/.profile
# Add poetry to the 'PATH' environment variable (1.1.10)
ENV PATH="/root/.poetry/bin:$PATH"

# NOTE: poetry version 1.2.0a2 automatically add poetry (/root/.local/bin) to the 'PATH', so the following is not needed.
#               Add poetry to the 'PATH' environment variable (1.2.0a2)
#               ENV PATH="/root/.local/bin:$PATH"

# Set environment variable to tell poetry to install everything on system's python
ENV POETRY_VIRTUALENVS_CREATE=false

RUN set -ex && \
    # sanity checks
    poetry --version && \
    # configurate poetry to install everything on system's python
    poetry config virtualenvs.create false
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
RUN set -ex && \
    # poetry installations are not editable # NOTE(diegovalenzuelaiturra: 2021-11-23): this may not be true anymore
    # to avoid installing development packages, use 'poetry install --no-dev'
    POETRY_VIRTUALENVS_CREATE=false poetry install && \
    # sanity checks
    python3 -c "import teselagen" && \
    python3 -c "import teselagen; print('teselagen version: ', teselagen.__version__)" && \
    # remove cache files
    poetry cache clear --no-interaction --all "$(poetry cache list)"
# >>>>>> Install teselagen Library >>>>>>

# >>>>>> Generate Jupyter Config >>>>>>
ENV PATH="~/.local/bin/jupyter-notebook:$PATH"

RUN set -ex && \
    # sanity checks
    jupyter --version &&  \
    jupyter notebook --version && \
    # jupyter should have already been installed by the `poetry install` command
    jupyter notebook --generate-config
# >>>>>> Generate Jupyter Config >>>>>>

# # >>>>>> Install Jupyter Extensions >>>>>>
# RUN set -ex \
#     && pip install jupyter_contrib_nbextensions \
#     && jupyter contrib nbextension install --system \
#     && jupyter nbextensions_configurator enable --user
# This may also be a nice extension: https://github.com/damianavila/RISE
# # <<<<<< Install Jupyter Extensions <<<<<<

# >>>>>> Clean Up >>>>>>
ARG PATH_TO_EXAMPLES=teselagen/examples/
ARG PATH_TO_EXAMPLES_REQUIREMENTS=teselagen/examples/requirements.txt

RUN set -ex \
    mkdir -p /home/examples &&  \
    # After the installation, we copy the examples folder to the home directory of the container.
    rsync ${PATH_TO_EXAMPLES} /home/examples \
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

RUN set -ex && \
    # set on bash start script
    echo source "/tmp/on_bash_start.sh" >> ~/.bashrc && \
    # provide proper permissions
    chmod 775 /tmp/on_bash_start.sh && \
    # log permissions
    ls -lahG /tmp/on_bash_start.sh

# >>>>>> Entrypoint & Command >>>>>>
RUN set -ex && \
    # provide proper permissions
    chmod +x on_start.sh && \
    # log permissions
    ls -lahG /tmp/on_start.sh

# Set the default working directory for the container
WORKDIR /home/

# https://stackoverflow.com/a/55734437
# CMD exec /bin/sh -c "trap : TERM INT; (while true; do sleep 1000; done) & wait"
ENTRYPOINT ["/tmp/on_start.sh"]
# <<<<<< Entrypoint & Command <<<<<<
