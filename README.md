# TeselaGen Python API Client

The _TeselaGen Python API Client_ runs on Python **3.9+**

**NOTE :** All the following commands are supposed to be run on the _base_ directory, unless specified.

## Library Installation

This library contains the TeselaGen Python API Client.

To install it locally with pip:

```bash
pip3 install teselagen
```

## Use and login

Import the `teselagen` library:

```python
from teselagen.api import TeselaGenClient
```

Create an instance of the client:

```python
client = TeselaGenClient(host_url="https://<INSTANCE NAME>.teselagen.com/")
```

Then, login by using your user email and One Time Password (OTP). You can get one from `Settings`-> `API Password`
within the application. Alternatively ,you can use your application password.

```python
client.login(username="my@email.com", password="<OTP OR PASSWORD>")
```

Once you have logged in, you don't need to do it everytime. By default login token lasts for 1 week, but you can
change the duration on creation by specifying an expiration time:

```python
client.login(username="my@email.com", password="<OTP OR PASSWORD>", expiration_time="1d")
```

## Examples

Check out the [provided examples](https://github.com/TeselaGen/api-client/tree/master/teselagen/examples). To be able
to run them:

1. Clone or download `teselagen/examples`

1. Open any notebook in the `examples` folder with Jupyter Notebook

## Development

### Poetry virtual environment

For development you can just use the virtual environment created by poetry. To install the project within a virtual
environment, use at the project's root folder:

`poetry install`

### Dependencies

#### Install dependencies

If lock file exists (the lock file contains fixed versions of dependencies), the `poetry install` command will install
all dependencies according to the lock file (lock file **must** be added to the repo). If the file does not exist, it
will generate the lock file again.

#### Update dependencies

Use this command if you made changes on the dependencies at the `pyproject.toml` file:

```bash
poetry update
```

It is the equivalent to make an install after deleting the `lock` file.

### Tests

1. Add your credentials

   To run the tests, you must create a `.credentials` file containing the test _username_ and _password_, in the
   _root_ folder.

   The content of `.credentials` file should look similar to the following:

   ```JSON
       {
           "username" : "ReplaceWithYourUsername",
           "password" : "ReplaceWithYourPassword"
       }
   ```

   - **NOTE 1**: It should be a valid `JSON` file. `JSON with Comments` (`JSONC` ) format is not supported.
   - **NOTE 2**: You may also add a `host` field. It's value will be used as default host name.

   ```diff
   - DO NOT COMMIT THIS FILE : .credentials
   ```

1. Modify configuration

   You may modify some test configuration parameters by creating a `.test_configuration` file.
   This is a `JSON` formatted file, where you can edit the server name used for tests.
   This file must be stored next to `.credentials` file. Here is an example

   ```JSON
   {
     "host_url" : "https://platform.teselagen.com"
   }
   ```

   - **NOTE**: It should be a valid `JSON` file. `JSON with Comments` (`JSONC` ) format is not supported.

1. Run the tests

   ```bash
   cd /home && python3 setup.py test
   ```

   You may use the docker environment for testing. For that, first build the environment with `bash build.sh`.
   Then just run the container with `bash run_dev.sh`.
   Once inside (`docker exec -ti tgclient bash`), go to `home/` and you are ready to run the test command shown above.

### Publishing

Publishing is limited to administrators. PyPi publishing is made by using [poetry](https://python-poetry.org/docs/).

To publish:

1. Run `poetry build` from the project's root folder (same directory as `pyproject.toml`)

1. Be sure you have set the credentials with the api token:

```bash
poetry config pypi-token.pypi <TOKEN>
```

Ask for a token to administrators if needed

1. Publish (check you have set a new version tag in `pyproject.toml`):

```bash
poetry publish
```

### Notes

Default shell in `Ubuntu` is `dash`, to which `/bin/sh` is symlinked. But `dash` doesn't have the `pipefail` option.
That's why some of our shell scripts have the following line:

```bash
# pipefail is necessary to propagate exit codes (but it may not be supported by your shell)
bash | set -o pipefail > /dev/null 2>&1
```

For example, the following commands will list all options supported by `set` in each of the respective shells:

```bash
sh -c 'set -o'
dash -c 'set -o'
bash -c 'set -o'
zsh -c 'set -o'
```

So, in `Ubuntu` it may be recommended to use `bash` instead of `sh`.

```bash
bash some_shell_script.sh
```

Or, as follows:

```bash
. some_shell_script.sh
```

---
