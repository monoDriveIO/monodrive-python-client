"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
# lib
import json
import os
import time
import signal
import threading
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# src
from monodrive.simulator import Simulator
from monodrive.sensors import *

# constants
VERBOSE = True
DISPLAY = True

# global
lock = threading.RLock()
processing = 0
running = True
camera_frame = None
lidar_frame = None


def camera_on_update(frame: CameraFrame):
    """
    callback to process parsed camera data
    """
    if VERBOSE:
        print("Perception system with image size {0}".format(frame.image.shape))
    global camera_frame
    camera_frame = frame
    with lock:
        global processing
        processing -= 1


def lidar_on_update(frame: LidarFrame):
    """
    callback to process parsed lidar data
    """
    if VERBOSE:
        print("LiDAR point cloud with size {0}".format(len(frame.points)))
    global lidar_frame
    lidar_frame = frame
    with lock:
        global processing
        processing -= 1


def state_on_update(frame: StateFrame):
    """
    callback to process parsed state sensor data
    """
    if VERBOSE:
        print("State sensor reporting {0} objects".format(len(frame.object_list)))
    with lock:
        global processing
        processing -= 1


def collision_on_update(frame: CollisionFrame):
    """
    callback to process parsed collision sensor data
    """
    if VERBOSE:
        collision = any([t.collision for t in frame.targets])
        nearest = min([t.distance for t in frame.targets], default=-1.0)
        print("Collision sensor: collision {}, nearest: {:.2f}m".format(collision, nearest))
    with lock:
        global processing
        processing -= 1


def main():
    """
    main driver function
    """
    root = os.path.dirname(__file__)

    # Flag to allow user to stop the simulation from SIGINT
    global running

    def handler(signum, frame):
        """"Signal handler to turn off the simulator with ctl+c"""
        global running
        running = False

    signal.signal(signal.SIGINT, handler)

    # Construct simulator from file
    simulator = Simulator.from_file(
        os.path.join(root, 'configurations', 'simulator.json'),
        trajectory=os.path.join(root, 'scenarios', 'replay_highway_exit.json'),
        sensors=os.path.join(root, 'configurations', 'sensors.json'),
        weather=os.path.join(root, 'configurations', 'weather.json'),
        ego=os.path.join(root, 'configurations', 'vehicle.json'),
        verbose=VERBOSE
    )

    # Start the simulation
    simulator.start()
    print('Starting simulator')
    try:
        # Subscribe to sensors of interest
        simulator.subscribe_to_sensor('Camera_8000', camera_on_update)
        simulator.subscribe_to_sensor('Lidar_8200', lidar_on_update)
        simulator.subscribe_to_sensor('State_8700', state_on_update)
        simulator.subscribe_to_sensor('Collision_8800', collision_on_update)

        # Start stepping the simulator
        time_steps = []

        # setup display
        if DISPLAY:
            fig = plt.figure('perception system', figsize=(10, 4))
            ax_camera = fig.add_subplot(1, 2, 1)
            ax_lidar = fig.add_subplot(1, 2, 2, projection='3d')
            ax_lidar.set_xlim3d(-20000, 20000)
            ax_lidar.set_ylim3d(-20000, 20000)
            ax_lidar.set_zlim3d(-5000, 5000)

            ax_lidar.set_axis_off()
            ax_camera.set_axis_off()

            fig.canvas.draw()
            data_camera = None
            data_lidar = None

        for i in range(simulator.num_steps):
            start_time = time.time()

            # expect 4 sensors to be processed
            with lock:
                global processing
                processing = 4

            # send step command
            response = simulator.step()

            # wait for processing to complete
            while running:
                with lock:
                    if processing == 0:
                        break
                time.sleep(0.05)

            # plot if needed
            if DISPLAY:
                global camera_frame, lidar_frame
                # update with camera data
                if camera_frame:
                    im = np.squeeze(camera_frame.image[..., ::-1])
                    if data_camera is None:
                        data_camera = ax_camera.imshow(im)
                    else:
                        data_camera.set_data(im)
                # update with lidar data
                if lidar_frame:
                    data = np.array([[pt.x, pt.y, pt.z, pt.intensity] for pt in lidar_frame.points])
                    data = data[np.any(data != 0, axis=1)]
                    if data_lidar is None:
                        data_lidar = ax_lidar.scatter(
                            data[:, 0], data[:, 1], data[:, 2],
                            s=0.1
                        )
                    else:
                        data_lidar._offsets3d = (data[:, 0], data[:, 1], data[:, 2])

                # do draw
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.0001)

            # timing
            dt = time.time() - start_time
            time_steps.append(dt)
            if VERBOSE:
                print("Step = {0} completed in {1:.2f}ms".format(i, (dt * 1000), 2))
                print("------------------")
            # time.sleep(1)
            if running is False:
                break

        fps = 1.0 / (sum(time_steps) / len(time_steps))
        print('Average FPS: {}'.format(fps))

    except Exception as e:
        print(e)

    print("Stopping the simulator.")
    simulator.stop()


if __name__ == "__main__":
    main()
