"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
# lib
import json
import os
import time
import signal
import matplotlib.pyplot as plt

# src
from monodrive.simulator.simulator import Simulator
from monodrive.sensors import *


def perception_on_update(frame):
    if frame:
        im = frame[0].image[..., ::-1]
        print("Perception system with image size {0}".format(im.shape))
        plt.imshow(im)  # TODO -- put this call on main thread
        plt.draw()
        plt.pause(0.0001)
        plt.clf()
    else:
        print("no image")


def reporting_on_update(data):
    print("Reporting Data *********** {0}".format(data[0].frame))


if __name__ == "__main__":
    root = os.path.dirname(__file__)

    # Flag to allow user to stop the simulation from SIGINT
    running = True


    def handler(signum, frame):
        """"Signal handler to turn off the simulator with ctl+c"""
        global running
        running = False


    signal.signal(signal.SIGINT, handler)

    # Construct simulator from file
    simulator = Simulator.from_file(
        os.path.join(root, 'configurations', 'simulator.json'),
        trajectory=os.path.join(root, 'trajectories', 'HighWayExitReplay.json'),
        sensors=os.path.join(root, 'configurations', 'all_sensors.json'),
        weather=os.path.join(root, 'configurations', 'weather.json'),
        ego=os.path.join(root, 'configurations', 'vehicle.json')
    )

    # Start the simulation
    simulator.start()

    # Subscribe to sensors of interest
    simulator.subscribe_to_sensor('Camera_8000', perception_on_update)
    simulator.subscribe_to_sensor('Collision_8800', reporting_on_update)

    # Start stepping the simulator
    time_steps = []
    for i in range(simulator.num_steps - 1):
        start_time = time.time()
        response = simulator.step()
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
