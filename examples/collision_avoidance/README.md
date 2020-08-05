# Simple collision UUT example

### Replay - prediction
Simple collision prediction system being tested against the monodrive simulator
in replay step mode

The Lidar sensor is used to predict whether a collision will occur,
which is then validated by the Collision sensor as ground truth.
The Collision sensor is also used to trigger early stopping
of the job.

The two example replays included here are
- Car-to-Car Rear Moving, Noncollision at 30km/h
- Car-to-Car Rear Moving, Collision at 30km/h

### Closed loop - AEBS
Simple collision avoidance system being tested against the monodrive simulator
in closed loop mode

The Lidar sensor is used to predict whether a collision will occur,
which triggers emergency braking.
The system is validated by the Collision sensor as ground truth.


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
python replay_prediction.py
```

## Build docker image
Build image
```
docker build -t monodrive-examples/collision:0.0  .
```
