# Simple collision UUT example
Simple collision prediction system being tested against the monodrive simulator
in replay step mode

The Lidar sensor is used to predict whether a collision will occur,
which is then validated by the Collision sensor as ground truth.
The Collision sensor is also used to trigger early stopping
of the job.

The two example scenarios included here are
- Car-to-Car Rear Moving, Noncollision at 30km/h
- Car-to-Car Rear Moving, Collision at 30km/h

## Requirements
Use [Conda](https://docs.conda.io/projects/conda/en/latest/)
to create Python virtual environment
```
conda env create --file environment.yml
```

Activate environment
```
conda activate uut-collision
```

## Run
Run driver script
```
python main.py
```

## Build docker image
Enable new docker build kit
```powershell
$env:DOCKER_BUILDKIT=1
```

Build image, passing in credentials for ssh-forwarding
```powershell
docker build --ssh default=C:\Users\devin\.ssh\id_rsa -t uut_examples/collision:0.0  .
```

*Note: the extra steps/args for ssh authentication are only temporary until the python client
is hosted on public pip*
