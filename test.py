"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
import json
import os
import time
import signal

from monodrive.simulator import Simulator
from uut.vehicle import Vehicle


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
    simulator = Simulator(sim_config, trajectory)

    # Load and configure the weather conditions for the simulator
    weather = json.load(
        open(os.path.join(root, 'configurations', 'weather.json')))
    profile = weather['profiles'][10]
    profile['id'] = 'test'

    # Start the simulation
    simulator.start()

    # Load the sensor configuration and software under test
    sensor_config = json.load(open(os.path.join(root, 'uut', 'sensor_config.json')))
    vehicle = Vehicle(sim_config, sensor_config)
    vehicle.start()

    # Start stepping the simulator
    for i in range(0, len(trajectory)-1):
        start_time = time.time()
        response = vehicle.step()
        print("Step = {0}".format(i))
        if running is False:
            break
        print("Frame Time = {0}".format(time.time() - start_time))

    print("Stopping the simulator.")
    simulator.stop()
    print("Stopping the uut.")
    vehicle.stop()

