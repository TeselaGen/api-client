FROM ubuntu:18.04

# Enable the non interactive frontend for automatic installs, which accepts all default answers to questions.
ARG DEBIAN_FRONTEND=noninteractive

# Enable terminal colors
ENV TERM=xterm-color
ENV COLORTERM=truecolor

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

# We set the user as "root" during the building process
USER root
EXPOSE 8888

RUN set -e \
    && apt-get update \
    # Configure Python3.9 repo on the system
    && apt install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/*

# Install python3.9
RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    # install Python3 (and pip3)
    python3.9 \
    python3-pip \
    # Create symbolic links:
    #   python -> python3
    #   pip -> pip3
    && ln -sfn /usr/bin/python3.9 /usr/bin/python \
    && ln -sfn /usr/bin/python3.9 /usr/bin/python3 \
    && ln -s /usr/bin/pip3 /usr/bin/pip \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/*

# We install needed dependencies
RUN set -x \
    && apt-get update \
    && apt-get install -yq \
    # --no-install-recommends \
    apt-utils \
    python3.9-distutils \
    # python3-setuptools \
    # python3 \
    # python3-pip \
    python3-venv \
    # install data transfer tool (and other required packages)
    ca-certificates curl gnupg2 \
    wget \
    nano \
    bzip2 \
    sudo \
    fonts-liberation \
    run-one \
    htop \
    rsync \
    # ensure to remove package's state information (it can be recreated with 'apt-get update')
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN set -x \
    # upgrade 'pip', 'setuptools', 'wheel'
    #   pip==21.1.3 setuptools==57.2.0 wheel==0.33.6
    && python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install poetry
RUN set -x \
    && apt-get update \
    && apt-get install -y curl \
    && curl -sSL  https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -o get-poetry.py \
    && python3 get-poetry.py --version 1.1.11
#     && rm -rf get-poetry.py
ENV PATH="/root/.poetry/bin:$PATH"

# Tell poetry to install everything on system's python
RUN set -x \
    poetry config virtualenvs.create false

# We set the current working directory
WORKDIR /tmp

# We copy files from the local folder to the working directory
COPY . .

# We define some PATHs arguments
ARG PATH_TO_EXAMPLES=lib/teselagen/examples/
ARG PATH_TO_MODULE_REQUIREMENTS=lib/requirements.txt
ARG PATH_TO_EXAMPLES_REQUIREMENTS=lib/teselagen/examples/requirements.txt

# Poetry installations are not editable
RUN set -x \
    cd lib/ \
    && POETRY_VIRTUALENVS_CREATE=false poetry install \
    && cd ..

# Generate Jupyter Config
ENV PATH="~/.local/bin/jupyter-notebook:$PATH"
RUN set -x \
    jupyter notebook --generate-config

# # >>>>>> Install Jupyter Extensions >>>>>>
# RUN set -x \
#     pip install jupyter_contrib_nbextensions \
#     && jupyter contrib nbextension install --system \
#     && jupyter nbextensions_configurator enable --user
# # <<<<<< Install Jupyter Extensions <<<<<<

# After the installation, we copy the examples folder to the home directory and then we delete the content of the
# working directory that was used for building and installing everything.
RUN set -x \
    rsync ${PATH_TO_EXAMPLES} /home/ \
    --human-readable \
    --progress \
    --perms \
    --executability  \
    --recursive \
    --exclude "*requirements.txt"

# Delete all from the local folder, except the file with the given name.
# RUN find . \! -name "*start.sh" -delete

# Set on bash start script
RUN set -x \
    echo source "/tmp/on_bash_start.sh" >> ~/.bashrc \
    && chmod 775 /tmp/on_bash_start.sh

# Entry point
RUN set -x \
    chmod +x on_start.sh

# And we set the "home" as the default working directory
WORKDIR /home/

ENTRYPOINT ["/tmp/on_start.sh"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]
