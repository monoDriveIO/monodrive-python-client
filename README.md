# monoDrive Python client

This repository contains a Python implementation of a client that can connect
to the monoDrive simulator, configure scenarios, and process sensor data.

## Usage
Simple quickstart example
```python
# TODO
```

You will need to have a monoDrive simulator running and available.
More detailed examples can be found in the `examples/` directory.

## Installation
Use [pip](https://pip.pypa.io/en/stable/installing/) for installation. We recommend you
do so within a virtual environment such as [Conda](https://docs.conda.io/en/latest/).

From pypi repositories (not yet supported)
```
pip install monodrive
```
From remote github repo
```
pip install git+git://github.com/monodriveIO/python_client.git@mycommit#egg=monodrive
```
From local github repo (when doing development)
```
pip install -e .
```

## Tips and troubleshooting

- If the simulator is running on another machine, you will need to update the
host information in `simulator.json`
```json
"simulator_ip": <IP OF SIMULATOR MACHINE>
```

- On running the script, you should see that the client is successfully connected to the simulator
and begins replaying the trajectory file.
