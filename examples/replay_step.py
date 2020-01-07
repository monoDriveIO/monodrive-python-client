"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
# lib
import json
import os
import time
import signal
import threading
import matplotlib.pyplot as plt

# src
from monodrive.simulator import Simulator
from monodrive.sensors import *

# global
lock = threading.RLock()
processing = 0


def camera_on_update(frame: CameraFrame):
    # im = frame.image[..., ::-1]
    print("Perception system with image size {0}".format(0))
    # plt.imshow(im)  # TODO -- put this call on main thread
    # plt.draw()
    # plt.pause(0.0001)
    # plt.clf()
    with lock:
        global processing
        processing -= 1
        print(processing)


def lidar_on_update(frame: LidarFrame):
    print("LiDAR point cloud with size {0}".format(len(frame.points)))
    with lock:
        global processing
        processing -= 1
        print(processing)


def state_on_update(frame: StateFrame):
    print("State sensor reporting {0} objects".format(len(frame.object_list)))
    with lock:
        global processing
        processing -= 1
        print(processing)


def collision_on_update(frame: CollisionFrame):
    print("Reporting collision {0}".format(frame.collision))
    with lock:
        global processing
        processing -= 1
        print(processing)


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
    simulator.subscribe_to_sensor('Camera_8000', camera_on_update)
    simulator.subscribe_to_sensor('Lidar_8200', lidar_on_update)
    simulator.subscribe_to_sensor('State_8700', state_on_update)
    simulator.subscribe_to_sensor('Collision_8800', collision_on_update)

    # Start stepping the simulator
    time_steps = []

    for i in range(simulator.num_steps):
        start_time = time.time()

        # expect 4 sensors to be processed
        with lock:
            processing = 4

        # send step command
        response = simulator.step()

        # wait for processing to complete
        while running:
            with lock:
                if processing == 0:
                    break
            time.sleep(0.05)

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
