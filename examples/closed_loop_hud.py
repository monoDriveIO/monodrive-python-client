"""
Closed Loop HUD example
An example of creating a viewport camera on the simulator with the vehicle
HUD enabled. The HUD is displayed on the simulator viewport only.
The values on the HUD can be updated with the ID_AUTOPILOT_CONTROL_COMMAND
command as shown below.
"""
# lib
import json
import os
import time
import signal
import threading
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# src
from monodrive.simulator import Simulator
from monodrive.sensors import *
import monodrive.common.messaging as mmsg

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
    global camera_frame
    camera_frame = frame
    with lock:
        global processing
        processing -= 1


def perception_and_control():
    # TODO, process sensor data and determine control values to send to ego
    return 0.4, 0, 0, 1  # fwd, right, brake, mode


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
        os.path.join(root, 'configurations', 'simulator_closed_loop.json'),
        scenario=os.path.join(root, 'scenarios', 'closed_loop.json'),
        sensors=os.path.join(root, 'configurations', 'sensors_hud.json'),
        weather=os.path.join(root, 'configurations', 'weather.json'),
        verbose=VERBOSE
    )

    # Start the simulation
    simulator.start()
    print('Starting simulator')
    try:
        # Subscribe to sensors of interest
        simulator.subscribe_to_sensor('Camera_8000', camera_on_update)

        # Start stepping the simulator
        time_steps = []

        # setup display
        if DISPLAY:
            fig = plt.figure('perception system', figsize=(5, 5))
            ax_camera = fig.add_subplot(1, 1, 1)
            ax_camera.set_axis_off()

            fig.canvas.draw()
            data_camera = None

        i = 0
        while running and i < 100:
            start_time = time.time()

            # expect 1 sensor to be processed
            with lock:
                global processing
                processing = 1

            # compute and send vehicle control command
            forward, right, brake, drive_mode = perception_and_control()
            if VERBOSE:
                print("sending control: {0}, {1}, {2}, {3}".format(
                    forward, right, brake, drive_mode
                ))

            response = simulator.send_control(forward, right, brake, drive_mode)
            if VERBOSE:
                print(response)

            response = simulator.sample_sensors()
            if VERBOSE:
                print(response)

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
                    im = np.squeeze(camera_frame.image[..., ::-1])
                    if data_camera is None:
                        data_camera = ax_camera.imshow(im)
                    else:
                        data_camera.set_data(im)

                # do draw
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.0001)

            # send autopilot command every twenty frames to update the HUD
            if i % 20 == 0:
                set_speed = random.randrange(1000, 4000)
                negotiated_speed = random.randrange(1000, 4000)
                autopilot_engaged = True if random.random() > 0.4 else False
                gear = random.choice(["1", "2", "3", "4"])
                lane_change = random.choice([-1, 0, 1])
                drive_mode = random.choice(["D", "R", "N", "P"])
                manual = not autopilot_engaged
                response = simulator.send_command(
                    mmsg.ApiMessage(
                        mmsg.ID_AUTOPILOT_CONTROL_COMMAND,
                        {
                            "set_speed": set_speed,
                            "negotiated_speed": negotiated_speed,
                            "autopilot_engaged": autopilot_engaged,
                            "gear": gear,
                            "lane_change": lane_change,
                            "drive_mode": drive_mode,
                            "manual_override": manual
                        }))
                if VERBOSE:
                    print(response)

            # timing
            dt = time.time() - start_time
            time_steps.append(dt)
            if VERBOSE:
                print("Step = {0} completed in {1:.2f}ms".format(i, (dt * 1000), 2))
                print("------------------")
            # time.sleep(1)
            if running is False:
                break

            i = i + 1

        # brake!
        simulator.send_control(0, 0, 1, 1)

        fps = 1.0 / (sum(time_steps) / len(time_steps))
        print('Average FPS: {}'.format(fps))
    except Exception as e:
        print(e)

    print("Stopping the simulator.")
    simulator.stop()


if __name__ == "__main__":
    main()
