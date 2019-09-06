"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
import json
import os
import time
import signal
import numpy as np
from itertools import combinations
from collections import defaultdict

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
    sensor_counts = defaultdict(int)
    sensor_json = []
    for sensor in sensors:
        print(sensor)
        with open(os.path.join(base_dir, sensor + ".json"), "r") as f:
            data = json.loads(f.read())
            data['listen_port'] += sensor_counts[sensor]
            sensor_json.append(data)
            sensor_counts[sensor] += 1

    return sensor_json


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
    stats["type"] = "stats"
    stats["total_time"] = total_time
    stats["fps"] = frame_times
    stats["avg_fps"] = 1.0 / np.mean(np.array(frame_times))

    simulator.stop()
    vehicle.stop()

    return stats


def run_single_trial(output_prefix: str, sim_config: dict, trajectory: dict,
                         weather: dict, sensors: list,
                         trajectory_name: str = "") -> None:
    output_filename = output_prefix + ".json"
    if os.path.exists(output_filename):
        return
    sensor_config = build_sensor_config(
        sensors, base_dir=os.path.join(root, "sensors"))
    stats = run_trial(sim_config, sensor_config, trajectory, weather)
    stats["trajectory"] = trajectory_name
    sensor_config.append(stats)
    write_results(output_filename, sensor_config)
    time.sleep(1)


def run_all_combos(output_prefix: str, sim_config: dict, trajectory: dict,
                   weather: dict) -> None:
    count = 0
    for i in range(1, len(avail_sensors)+1):
        for combo in combinations(avail_sensors, i):
            sensor_config = build_sensor_config(
                list(combo), base_dir=os.path.join(root, "sensors"))
            stats = run_trial(sim_config, sensor_config, trajectory, weather)

            with open(output_prefix + str(count).zfill(3) + ".json", "w") as f:
                f.write(json.dumps(sensor_config))
            count += 1
            time.sleep(1)

            if RUNNING is False:
                break


def run_multiple_sensors(output_prefix: str, sim_config: dict, trajectory: dict,
                         weather: dict, sensor: str, sensor_count: int,
                         trajectory_name: str = "") -> None:
    count = 0
    for i in range(1, sensor_count+1):
        output_filename = output_prefix + str(count).zfill(3) + ".json"
        count += 1
        if os.path.exists(output_filename):
            print(output_filename, "already exists")
            continue
        sensor_config = build_sensor_config(
            i*[sensor], base_dir=os.path.join(root, "sensors"))
        stats = run_trial(sim_config, sensor_config, trajectory, weather)
        stats["trajectory"] = trajectory_name
        sensor_config.append(stats)
        write_results(output_filename, sensor_config)
        time.sleep(1)


def write_results(filename: str, data: dict) -> None:
    with open(filename, "w") as f:
        f.write(json.dumps(data, sort_keys=True, indent=4,
                           separators=(',', ': ')))


if __name__ == "__main__":
    root = os.path.dirname(__file__)

    fps_trajectories = []
    for file in os.listdir("./fps_trajectories"):
        print("Loading:", file)
        fps_trajectories.append(os.path.join(root, "./fps_trajectories/", file))

    # Load the sensor configuration and software under test
    avail_sensors = ["Camera", "Collision", "GPS", "IMU", "Lidar", "Radar",
                     "RPM", "State"]

    sim_config = json.load(open(os.path.join(root, 'configurations',
                                             'simulator.json')))

    # Load and configure the weather conditions for the simulator
    weather = json.load(
        open(os.path.join(root, 'configurations', 'weather.json')))
    profile = weather['profiles'][10]
    profile['id'] = 'test'

    # sensors = ["Camera256", "Collision", "GPS", "IMU", "Lidar16", "Radar",
    #            "RPM", "State"]
    # sensors = ["Camera512", "Collision", "GPS", "IMU", "Lidar16", "Radar",
    #            "RPM", "State"]
    #sensors = ["Camera768", "Collision", "GPS", "IMU", "Lidar16", "Radar",
               #"RPM", "State"]
    # sensors = ["Camera1024", "Collision", "GPS", "IMU", "Lidar16", "Radar",
    #            "RPM", "State"]
    #sensors = ["Collision", "GPS", "IMU", "Lidar16", "Radar", "RPM", "State"]
    # for traj in fps_trajectories:
    #     output_file = "./results/" + \
    #                   traj[traj.rfind("/") + 1:traj.rfind(".")] + \
    #                   "_full_suite_no_render_Lidar16"
    #     trajectory = json.load(open(traj, "r"))
    #     run_single_trial(output_file, sim_config, trajectory, weather,
    #                      sensors,  trajectory_name=traj)

    sensors = ["Radar"]
    trials = 10
    for sensor in sensors:
        for traj in fps_trajectories:
            print("Running trajectory:", traj)
            print("\tSensor:", sensor)
            print("\tTrials:", trials)
            # Load the trajectory and simulator configurations
            trajectory = json.load(open(traj, "r"))
            output_file = "./results/radar_results/" + \
                          traj[traj.rfind("/")+1:traj.rfind(".")] + \
                          "_no_render_multi_" + sensor + "_"
            run_multiple_sensors(output_file, sim_config, trajectory, weather,
                                 sensor, trials, trajectory_name=traj)
