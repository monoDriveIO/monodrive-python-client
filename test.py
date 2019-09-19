"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
import json
import os
import time
import signal

from monodrive.simulator import Simulator
from uut.vehicles.example_vehicle import ExampleVehicle

if __name__ == "__main__":
    root = os.path.dirname(__file__)

    # Flag to allow user to stop the simulation from SIGINT
    running = True


    def handler(signum, frame):
        """"Signal handler to turn off the simulator with ctl+c"""
        global running
        running = False


    signal.signal(signal.SIGINT, handler)

    # Load the trajectory and simulator configurations
    trajectory = json.load(open(os.path.join(root, 'configurations', 'trajectories', 'HighWayExitReplay.json')))
    sim_config = json.load(open(os.path.join(root, 'configurations', 'simulator.json')))

    # configure this simulator client
    # Load the reporting sensor configuration and software under test
    # reporting_config = json.load(open(os.path.join(root, 'monodrive', 'reporting_config.json')))
    simulator = Simulator(sim_config, trajectory)

    # Load and configure the weather conditions for the simulator
    weather = json.load(
        open(os.path.join(root, 'configurations', 'weather.json')))
    profile = weather['profiles'][10]
    profile['id'] = 'test'

    # Start the simulation
    simulator.start()

    # Load the sensor configuration and software under test
    sensor_config = json.load(open(os.path.join(root, 'uut', 'gps_config.json')))
    vehicle = ExampleVehicle(sim_config, sensor_config)

    vehicle.start()
    # vehicle.initialize_perception()
    vehicle.initialize_reporting()
    print(vehicle.sensors_ids)

    # Start stepping the simulator
    time_steps = []
    for i in range(0, len(trajectory) - 1):
        start_time = time.time()
        response = vehicle.step()
        dt = time.time() - start_time
        time_steps.append(dt)
        print("Step = {0} completed in {1:.2f}ms".format(i, (dt * 1000), 2))
        # time.sleep(1)
        if running is False:
            break

    fps = 1.0 / (sum(time_steps) / len(time_steps))
    print('Average FPS: {}'.format(fps))

    print("Stopping the simulator.")
    simulator.stop()
    print("Stopping the uut.")
    vehicle.stop()
