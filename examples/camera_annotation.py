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
import cv2

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


def camera_on_update(frame: CameraFrame):
    """
    callback to process parsed camera data
    """
    if VERBOSE:
        print("Perception system with image size {0}".format(frame.image.shape))
        if frame.annotation:
            print("Annotation info: \n{0}".format(frame.annotation))
    global camera_frame

    camera_frame = frame
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
        os.path.join(root, 'configurations', 'annotated_camera_simulator.json'),
        trajectory=os.path.join(root, 'trajectories', 'tcd_replay_60mph_short.json'),
        sensors=os.path.join(root, 'configurations', 'annotated_camera_sensors.json'),
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
        # simulator.subscribe_to_sensor('State_8700', state_on_update)

        # Start stepping the simulator
        time_steps = []

        # setup display
        if DISPLAY:
            fig = plt.figure('image annotations', figsize=(12, 12))
            # fig = plt.figure('image annotations', figsize=(6, 6))
            ax_camera = fig.gca()
            ax_camera.set_axis_off()

            fig.canvas.draw()
            data_camera = None

        for i in range(simulator.num_steps):
            start_time = time.time()

            # expect 2 sensors to be processed
            with lock:
                global processing
                processing = 1

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
                global camera_frame
                # update with camera data
                if camera_frame:
                    img = np.array(camera_frame.image[..., ::-1])
                    for actor_annotation in camera_frame.annotation:
                        for primitive_annotation in actor_annotation["2d_bounding_boxes"]:
                            box = primitive_annotation["2d_bounding_box"]
                            top_left = (int(box[0]), int(box[2]))
                            bottom_right = (int(box[1]), int(box[3]))
                            cv2.rectangle(img, top_left, bottom_right, (255, 0, 0), 1)

                    if data_camera is None:
                        data_camera = ax_camera.imshow(img)
                    else:
                        data_camera.set_data(img)

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
