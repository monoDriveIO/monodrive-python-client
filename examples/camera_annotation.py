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
import matplotlib.pyplot as plt
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
semantic_frame = None


def camera_on_update(frame: CameraFrame):
    """
    callback to process parsed camera data
    """
    if VERBOSE:
        print("Camera frame with RGB image size {0}".format(frame.image.shape))
        if frame.annotation:
            print("Annotation info: \n{0}".format(frame.annotation))
    global camera_frame
    camera_frame = frame
    with lock:
        global processing
        processing -= 1


def semantic_on_update(frame: CameraFrame):
    """
    callback to process parsed semantic camera frame
    """
    if VERBOSE:
        print("Camera frame with semantic image size {0}".format(frame.image.shape))
    global semantic_frame
    semantic_frame = frame
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
        os.path.join(root, 'configurations', 'simulator_annotated_camera.json'),
        scenario=os.path.join(root, 'scenarios', 'replay_tcd_60mph_short.json'),
        sensors=os.path.join(root, 'configurations', 'sensors_annotated_camera.json'),
        weather=os.path.join(root, 'configurations', 'weather.json'),
        verbose=VERBOSE
    )

    # Start the simulation
    simulator.start()
    print('Starting simulator')
    try:
        # Subscribe to sensors of interest
        simulator.subscribe_to_sensor('Camera_8000', camera_on_update)
        simulator.subscribe_to_sensor('SemanticCamera_8001', semantic_on_update)

        # Start stepping the simulator
        time_steps = []

        # setup display
        if DISPLAY:
            fig = plt.figure('image annotations', figsize=(16, 8))
            ax_camera = fig.add_subplot(1, 2, 1)
            ax_semantic = fig.add_subplot(1, 2, 2)
            ax_camera.set_axis_off()
            ax_semantic.set_axis_off()

            fig.canvas.draw()
            data_camera = None
            data_semantic = None

        for i in range(simulator.num_steps):
            start_time = time.time()

            # expect 2 sensors to be processed
            with lock:
                global processing
                processing = 2

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
                            cv2.rectangle(img, top_left, bottom_right, (255, 0, 0), 2)

                    if data_camera is None:
                        data_camera = ax_camera.imshow(img)
                    else:
                        data_camera.set_data(img)

                if semantic_frame:
                    img = np.squeeze(semantic_frame.image)

                    if data_semantic is None:
                        data_semantic = ax_semantic.imshow(img)
                    else:
                        data_semantic.set_data(img)

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
