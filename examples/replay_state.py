"""
Replay state example

An example which configures the simulator in replay state mode,
creates and sets a series of programmatically defined frames,
and processes the sensor output.
"""

# lib
import os
import time
import json
import threading
from monodrive.simulator.simulator import Simulator
from monodrive.sensors import *

# global
lock = threading.RLock()
processing = 0
camera_frame: CameraFrame = None


def camera_on_update(frame: CameraFrame):
    """
    Callback to handle parsed Camera frame

    Args:
        frame: parsed Camera frame
    """
    # store
    global camera_frame
    camera_frame = frame

    print(frame)

    # done processing
    with lock:
        global processing
        processing -= 1


def main():
    """main test driver function"""

    # setup template for frame
    frame = {
        "frame": [
            {
                "name": "EgoVehicle",
                "orientation": [0.0, 0.0, 0.0, 1.0],
                "position": [17347.66, 17884.67, 13.4],
                "tags": ["ego", "vehicle", "dynamic"]
            }
        ],
        "game_time": 0.0,
        "sample_count": 0,
        "time": 1579283717
    }

    # configure simulator
    root = os.path.dirname(__file__)

    simulator = Simulator.from_file(
        os.path.join(root, 'configurations', 'simulator.json'),
        sensors=os.path.join(root, 'configurations', 'sensors.json'),
        weather=os.path.join(root, 'configurations', 'weather.json')
    )

    res = simulator.start()
    simulator.subscribe_to_sensor('Camera_8000', camera_on_update)

    try:
        for n in range(20):
            with lock:
                global processing
                processing = 1

            # move vehicle forward
            frame['frame'][0]['position'][0] += 100

            # set state
            res = simulator.send_state(frame)

            # wait for processing to complete
            while True:
                with lock:
                    if processing == 0:
                        break
                time.sleep(0.05)

    except Exception as e:
        print(e)

    simulator.stop()


if __name__ == '__main__':
    main()
