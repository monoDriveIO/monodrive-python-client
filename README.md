# monoDrive Python Client

This repository contains a Python implementation of client that can connect
to the monoDrive simulator and process sensor data. 

# Prerequisties

You'll need to use Python 3 or higher in order to use the client. To get 
started, just clone the repo, create a virtual environment and install the 
`requirements.txt`:

```bash
$ git clone git@github.com:monoDriveIO/python_client.git
$ cd ./python_client
$ virtualenv ./venv 
$ . ./venv/bin/activate
(venv) $ pip install -r ./requirements.txt
```

# Usage
There's an example usage of the simulator in `test.py`. You'll need to have
a monoDrive simulator running either locally or on the same network. If not
running the simulator locally, in `./configurations/simulator.json` make sure 
to set:

```json
"simulator_ip": <IP OF SIMULATOR MACHINE>
```

Now you can run the sample in `test.py`:

```bash
(venv) $ python ./test.py`
```

You should see that the client is successfully connected to the simulator and
begins replaying the trajectory from 
`./configurations/open_sense/SuddenStop.json`.
