# Simple collision UUT example

This example uses the `jobs` module to support local and cloud batch processing.

### Replay - prediction
Simple collision prediction system being tested against the monodrive simulator
in replay step mode

The Ultrasonic sensor is used to predict whether a collision will occur,
which is then validated by the Collision sensor as ground truth.
The Collision sensor is also used to trigger early stopping
of the job.

The two example replays included here are
- Car-to-Car Rear Moving, Noncollision at 30km/h
- Car-to-Car Rear Moving, Collision at 30km/h

### Closed loop - AEBS
Simple collision avoidance system being tested against the monodrive simulator
in closed loop mode

The Ultrasonic sensor is used to predict whether a collision will occur,
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
Run single replay prediction job for development
```
python replay_prediction.py --md_simulator ../configurations/simulator.json --md_scenario ../scenarios/replay_ncap_ccrm_collision_30km.json --md_weather ../configurations/weather.json --md_sensors ../configurations/sensors.json --md_results ./test_results.json
```
Run single AEBS job for development
```
python closed_loop_aebs.py --md_simulator ../configurations/simulator.json --md_scenario ../scenarios/scenario_aebs.json --md_weather ../configurations/weather.json --md_sensors ../configurations/sensors_collision.json --md_results ./test_results.json --throttle 0.6
```

Run continuously for local batch processing
```
python replay_prediction.py --md_assets ./assets_dir --md_loop
```

For more usage info on the `monodrive.jobs` module
```
python replay_prediction --md_help
```

## Build docker image
Build image
```
docker build -t monodrive-examples/collision:0.0  .
```
