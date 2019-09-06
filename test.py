"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
import json
import os
import time
import signal
import numpy as np
from itertools import combinations

from monodrive.simulator import Simulator
from uut.vehicles.example_vehicle import ExampleVehicle

# Flag to allow user to stop the simulation from SIGINT
RUNNING = True

def handler(signum, frame):
    """"Signal handler to turn off the simulator with ctl+c"""
    global RUNNING
    RUNNING = False


signal.signal(signal.SIGINT, handler)


def build_sensor_config(sensors: list, base_dir: str = "./sensors/") -> dict:
    sensor_json = "["
    for sensor in sensors:
        with open(os.path.join(base_dir, sensor + ".json"), "r") as f:
            sensor_json += f.read() + ","

    sensor_json = sensor_json[:-1] + "]"
    print(sensor_json)

    return json.loads(sensor_json)

def run_trial(sim_config: dict, sensor_config: dict, trajectory: dict,
              weather: dict) -> dict:
    global RUNNING

    # configure this simulator client
    # Load the reporting sensor configuration and software under test
    simulator = Simulator(sim_config, trajectory)

    # Start the simulation
    simulator.start()

    vehicle = ExampleVehicle(sim_config, sensor_config)
    vehicle.start()

    # Start stepping the simulator
    start_time = time.time()
    frame_times = []

    # Run through every step in the trajectory
    for i in range(0, len(trajectory) - 1):
        frame_start = time.time()
        response = vehicle.step()
        frame_times.append(time.time() - frame_start)
        if RUNNING is False:
            break

    total_time = time.time() - start_time
    stats = dict()
    stats["total_time"] = total_time
    stats["fps"] = frame_times
    stats["avg_fps"] = 1.0 / np.mean(np.array(frame_times))

    simulator.stop()
    vehicle.stop()

    return stats


if __name__ == "__main__":
    root = os.path.dirname(__file__)

    # Load the sensor configuration and software under test
    avail_sensors = ["Camera", "Collision", "GPS", "IMU", "Lidar", "Radar",
                     "RPM", "State"]
    # Load the trajectory and simulator configurations
    trajectory = json.load(open(os.path.join(root, 'configurations',
                                             'trajectories',
                                             'HighWayExitReplay.json')))
    sim_config = json.load(open(os.path.join(root, 'configurations',
                                             'simulator.json')))

    # Load and configure the weather conditions for the simulator
    weather = json.load(
        open(os.path.join(root, 'configurations', 'weather.json')))
    profile = weather['profiles'][10]
    profile['id'] = 'test'

    count = 0
    for i in range(1, len(avail_sensors)+1):
        for combo in combinations(avail_sensors, i):
            sensor_config = build_sensor_config(
                list(combo), base_dir=os.path.join(root, "sensors"))
            stats = run_trial(sim_config, sensor_config, trajectory, weather)

            with open("trial" + str(count).zfill(3) + ".json", "w") as f:
                f.write(json.dumps(sensor_config))
            count += 1

            if RUNNING is False:
                break
