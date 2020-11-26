# TeselaGen Python API Client.

The _TeselaGen Python API Client_ runs on Python 3.

**NOTE :** All the following commands are supposed to be run on the `base` directory, unless specified.

## Library Installation
This library contains the TeselaGen Python API Client.

To install it locally,

1. Install the requirements for the library. Go to `lib/' folder and:

    ```
    pip3 install --requirement ./requirements.txt --no-cache-dir
    ```

1. Install the library.

    ```
    python3 setup.py install
    ```

## Examples

To be able to run the `examples`, you need to

1. Install the requirements for the `examples`, located in the `./teselagen/examples/` folder.

    ```
    pip3 install --requirement ./teselagen/examples/requirements.txt --no-cache-dir
    ```

1. Open the Jupyter Notebook example

    If you are not using the provided docker environment (see docker_environment folder), first install jupyter in your own environment (if you don't have it yet). You can specify the port the notebook server will listen on, by using the following flag `--port:PORT`. Just replace `PORT` value with your own.

    For example, by running the following command, the Jupyter Notebook example may start running on port `8888`

    ```
    jupyter notebook ./teselagen/examples/Hello_World.ipynb --port 8888
    ```

    Access to it, opening a browser and going to the following address:

    ```
    http://localhost:8888
    ```

## Tests

1. Add your credentials

    To run the tests, you must create a `.credentials` file containing the test username and password, in the root  folder (`teselagenpy/lib`).

    The content of `.credentials` file should look similar to the following:

    ```
        {
            "username" : "ReplaceWithYourUsername",
            "password" : "ReplaceWithYourPassword"
        }
    ````

    ```diff
    - DO NOT COMMIT THIS FILE : .credentials
    ```

1. Modify configuration

    You may modify some test configuration parameters by creating a `.test_configuration` file. This is a
    `json` formatted file, where you can edit the server name used for tests. This file must be stored next to
    `.credentials` file. Here is an example

    ```
    {
	    "host_url" : "https://platform.teselagen.com"
    }
    ```

1. Run the tests (on `/lib` folder)

    ```
    python3 setup.py test
    ```

    You may use the docker environment for testing. For that, first build the environment with `sh build.sh` at
    the `docker_environment` folder. Then just run the container with `sh run_dev.sh`. Once inside (`docker exec -ti tgclient bash`), go to
    `home/development/lib` and you are ready to run the test command shown above.


