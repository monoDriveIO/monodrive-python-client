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


def camera_on_update(frame: CameraFrame):
    """
    Callback to handle parsed Camera frame

    Args:
        frame: parsed Camera frame
    """
    print('received image frame: {}'.format(frame.image.shape))

    # done processing
    with lock:
        global processing
        processing -= 1


def state_on_update(frame: StateFrame):
    """
    callback to process parsed state sensor data
    """
    ego_state = None
    for v in frame.frame.vehicles:
        if 'ego' in v.state.tags:
            ego_state = v
    print('ego pose: {}'.format(ego_state.state.odometry['pose']))
    with lock:
        global processing
        processing -= 1


def main():
    """main test driver function"""

    # setup template for frame
    frame = {
        "frame": {
            "vehicles": [
                {
                    "state": {
                        "name": "EgoVehicle",
                        "odometry": {
                            "pose": {
                                "orientation": {
                                    "w": 1.0,
                                    "x": 0.0,
                                    "y": 0.0,
                                    "z": 0.0
                                },
                                "position": {
                                    "x": 1400,
                                    "y": 600,
                                    "z": 13.5
                                }
                            }
                        },
                        "tags": ["vehicle", "dynamic", "car", "ego"]
                    }
                }
            ]
        },
        "game_time": 0.0,
        "sample_count": 0,
        "time": 1579283717
    }
    ego_pose = frame['frame']['vehicles'][0]['state']['odometry']['pose']

    # configure simulator
    root = os.path.dirname(__file__)

    simulator = Simulator.from_file(
        os.path.join(root, 'configurations', 'simulator.json'),
        sensors=os.path.join(root, 'configurations', 'sensors.json'),
        weather=os.path.join(root, 'configurations', 'weather.json'),
        verbose=True
    )

    res = simulator.start()
    simulator.subscribe_to_sensor('Camera_8000', camera_on_update)
    simulator.subscribe_to_sensor('State_8700', state_on_update)

    try:
        for n in range(100):
            with lock:
                global processing
                processing = 2

            # move vehicle forward
            ego_pose['position']['x'] += 50

            # set state
            print('step: {}'.format(n))
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
