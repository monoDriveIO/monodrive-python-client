"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
import json
import os
import time
import signal

from monodrive.simulator import Simulator


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
    trajectory = json.load(
        open(os.path.join(
            root, 'configurations', 'open_sense', 'SuddenStop.json')))
    simulator = Simulator(
        json.load(open(os.path.join(root, 'configurations', 'simulator.json'))),
        json.load(open(os.path.join(root, 'configurations', 'sensors.json'))),
        trajectory)

    # Load and configure the weather conditions for the simulator
    weather = json.load(
        open(os.path.join(root, 'configurations', 'weather.json')))
    profile = weather['profiles'][10]
    profile['id'] = 'test'

    # Start the simulation
    simulator.start()
    # Give the server a little time to load up
    print("Sleeping for 10 seconds to allow the simulator to start.")
    time.sleep(10)
    # Continue to step through the replay simulation
    print("Stepping the simulator.")
    for i in range(0, len(trajectory)):
        simulator.step()
        time.sleep(.25)
        print("Step.")
        if running is False:
            break
    print("Stopping the simulator.")
    simulator.stop()
