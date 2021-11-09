# TeselaGen Python API Client.

The _TeselaGen Python API Client_ runs on Python 3.

**NOTE :** All the following commands are supposed to be run on the `base` directory, unless specified.

## Library Installation
This library contains the TeselaGen Python API Client.

To install it locally,

1. Install it with pip

    ```bash
    pip3 install teselagen
    ```

## Examples

To be able to run the `examples`, you need to (after installing the library)

1. Clone or download `lib/examples`

1. Open any notebook in the `examples` folder with Jupyter Notebook

## Use the provided environment

You can use the provided docker environment that contains a ready to use installation of all required packages to run the notebooks. Here are the instructions according to your OS

### Linux/MacOS

1. After clone/download, go to `docker_environment` and run the build script with `sh build.sh`

1. Run the container with `sh run.sh`

1. Open your browser and set the address: `http://localhost:8888`. From there you can explore all example notebooks

## Development (Linux/MacOS)

### Docker environment

1. Build the docker environment with command `sh build.sh`

2. Run the container as a developer with the command `sh run_dev.sh`. With this command the `teselagen` library will be installed in [editable](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) mode.

### Dependencies

#### Install dependencies

If lock file exists (the lock file contains fixed versions of dependencies), the `poetry install` command will install all dependencies according to the lock file (lock file **must** be added to the repo). If the file does not exist, it will generate the lock file again.

#### Update dependencies

Use this command if you made changes on the dependencies at the *toml* file:
```bash
poetry update
```

It is the equivalent to make an install after deleting the `lock` file.

### Tests

1. Add your credentials

    To run the tests, you must create a `.credentials` file containing the test username and password, in the root folder (`teselagenpy/lib`).

    The content of `.credentials` file should look similar to the following:

    ```JSON
        {
            "username" : "ReplaceWithYourUsername",
            "password" : "ReplaceWithYourPassword"
        }
    ````

    ```diff
    - DO NOT COMMIT THIS FILE : .credentials
    ```

1. Modify configuration

    You may modify some test configuration parameters by creating a `.test_configuration` file. This is a `json` formatted file, where you can edit the server name used for tests. This file must be stored next to `.credentials` file. Here is an example

    ```JSON
    {
	    "host_url" : "https://platform.teselagen.com"
    }
    ```

1. Run the tests (on `/lib` folder)

    ```bash
    python3 setup.py test
    ```

    You may use the docker environment for testing. For that, first build the environment with `sh build.sh` at the `docker_environment` folder. Then just run the container with `sh run_dev.sh`. Once inside (`docker exec -ti tgclient bash`), go to `home/development/lib` and you are ready to run the test command shown above.

### Publishing

Publishing is limited to administrators. PyPi publishing is made by using [poetry](https://python-poetry.org/docs/).

To publish:

1. Run `poetry build` from the project's root folder (same directory as *pyproject.toml*)

1. Be sure you have set the credentials with the api token:

```bash
poetry config pypi-token.pypi <TOKEN>
```

Ask for a token to administrators if needed

1. Publish (check you have set a new version tag in `pyproject.toml`):

```bash
poetry publish
```

---

<!--

# apply end-of-line normalization
git add --renormalize .

# run docstrings formatter
python3 -m docformatter --recursive --wrap-summaries 119 --wrap-descriptions 119 --in-place .

# sort imports
python3 -m isort --jobs=8 --color .

# run code formatter
python3 -m yapf --in-place --recursive --parallel .

# remove unused imports
python3 -m autoflake --verbose --remove-all-unused-imports --ignore-init-module-imports --recursive --in-place .

# run tests
cd /home/development/lib
python3 setup.py test

# run coverage
cd /home/development/lib
pytest --cov="teselagen" --cov-report term:skip-covered

-->
