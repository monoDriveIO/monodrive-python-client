# monoDrive Python client

This repository contains a Python implementation of a client that can connect
to the monoDrive simulator, configure scenarios, and process sensor data.

**NOTE:** The monoDrive Python client is intended for rapid prototype development and algorithm investigation. For a 
more performant, production-ready client, consider using the 
[monoDrive C++ Client](https://github.com/monoDriveIO/monodrive-client) or 
[monoDrive LabVIEW Client](https://monodrive.readthedocs.io/en/latest/LV_client/quick_start/LabVIEW_client_quick_start/).

## Installation
We recommend using an Anaconda environment for the simulator client. Instructions and download for the "Miniconda" 
version of Anaconda can be found [here](https://docs.conda.io/en/latest/miniconda.html). To setup a new environment
simply

```bash
$ conda create --name simulator-python-client python=3.7
$ conda activate simulator-python-client
(simulator-python-client) $
```

To install the monoDrive client from the remote github repo (where `mycommit` is the git hash you want to install):

```
(simulator-python-client) $ pip install git+git://github.com/monodriveIO/python_client.git@mycommit#egg=monodrive
```

Of to install it from the cloned repo:

```
(simulator-python-client) $ pip install -e .
```

## Usage

To run a simple closed loop example, start the monoDrive Simulator or Scenario Editor in PIE mode locally, then from
the activated and installed environment:

```python
(simulator-python-client) $ python ./examples/closed_loop.py
```

More detailed examples can be found in the `examples/` directory.

## Tips and Troubleshooting

- If the simulator is running on another machine, you will need to update the
host information in `simulator.json`

```json
"simulator_ip": <IP OF SIMULATOR MACHINE>
```

