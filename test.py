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
    trajectory = json.load(open(os.path.join(root, 'configurations', 'trajectories', 'HighWayExitReplay.json')))
    sim_config = json.load(open(os.path.join(root, 'configurations', 'simulator.json')))
    sensor_config = json.load(open(os.path.join(root, 'configurations', 'sensor_config_new.json')))

    # configure this simulator client
    simulator = Simulator(sim_config, sensor_config, trajectory)

    # Load and configure the weather conditions for the simulator
    weather = json.load(
        open(os.path.join(root, 'configurations', 'weather.json')))
    profile = weather['profiles'][10]
    profile['id'] = 'test'

    # Start the simulation
    simulator.start()

    simulator.start_sensor_listening()

    # Give the server a little time to load up
    #print("Sleeping for 1 second to allow the simulator to start.")
    #time.sleep(.1)
    # Continue to step through the replay simulation
    print("Stepping the simulator.")

    for i in range(0, len(trajectory)):
        start_time = time.time()
        response = simulator.step()
        print("Step = {0}".format(i))
        if running is False:
            break
        print("Frame Time = {0}".format(time.time() - start_time))
    print("Stopping the simulator.")
    simulator.stop()
