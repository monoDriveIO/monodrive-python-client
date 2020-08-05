"""
Simple collision prediction system being tested against the monodrive simulator
in replay step mode
"""

# lib
import os
import time
import json
import threading
import argparse
import numpy as np
from monodrive.simulator.simulator import Simulator
from monodrive.sensors import *
from monodrive.jobs import loop, set_result, Result, ResultMetric

# constants
PREDICT_WINDOW_MIN = 0.01  # 10ms
PREDICT_WINDOW_MAX = 1.0  # 1s

# global
lock = threading.RLock()
collision_occurred = None
collision_predicted = None
processing = 0
full_frames = []


def lidar_on_update(frame: LidarFrame):
    """
    Callback to process a parsed Lidar frame

    Attempt to predict when a collision will occur based on 3d point cloud
    information parsed from the Lidar data

    Args:
        frame: parsed Lidar frame
    """
    # compute nearest point
    points = np.array([[pt.x, pt.y, pt.z] for pt in frame.points])
    points = points[np.any(points != 0, axis=1)]
    distances = np.linalg.norm(points, axis=1)
    nearest = np.min(distances)

    # predict
    if nearest < 3000.0:
        global collision_predicted
        if collision_predicted is None:
            collision_predicted = frame.game_time
        print('Collision predicted, distance: {}, game time: {}'.format(nearest, frame.game_time))

    # done processing
    with lock:
        global processing
        processing -= 1


def collision_on_update(frame: CollisionFrame):
    """
    Callback to process a parsed Collision Sensor frame

    This serves as ground truth to validate the collision prediction system

    Args:
        frame: parsed Collision Sensor frame
    """
    # check for collision
    collision_in_frame = any([t.collision for t in frame.targets])
    if collision_in_frame:
        global collision_occurred
        collision_occurred = frame.game_time
        print('Collision detected at game time: {}'.format(frame.game_time))

    # append for full report
    full_frames.append(frame)

    # done processing
    with lock:
        global processing
        processing -= 1


def main_uut(simulator: Simulator, results_path: str, results_full_path: str):
    """main uut driver function"""

    # setup globals
    global collision_occurred, collision_predicted
    collision_occurred = None
    collision_predicted = None

    # start simulator and subscribe to sensors
    res = simulator.start()
    simulator.subscribe_to_sensor('Collision_8800', collision_on_update)
    simulator.subscribe_to_sensor('Lidar_8200', lidar_on_update)

    # UUT code
    for n in range(simulator.num_steps):
        print("**************************{0}******************************".format(n))

        # expect 2 sensors to be processed
        with lock:
            global processing
            processing = 2

        # send step command
        res = simulator.step()

        # wait for processing to complete
        while True:
            with lock:
                if processing == 0:
                    break
            time.sleep(0.05)

        if collision_occurred:
            print('Collision occurred - exiting early.')
            break

    simulator.stop()

    # pass/fail criteria
    if collision_predicted is None and collision_occurred is None:
        # true negative
        pass_result = True
    elif collision_predicted is None or collision_occurred is None:
        # false negative/positive
        pass_result = False
    else:
        delta = collision_occurred - collision_predicted
        print('Prediction time delta: {}'.format(delta))
        if PREDICT_WINDOW_MIN < delta < PREDICT_WINDOW_MAX:
            pass_result = True
        else:
            pass_result = False

    print('Test result: {}'.format('PASS' if pass_result else 'FAIL'))

    # write out full results
    with open(results_full_path, 'w') as file:
        file.write(json.dumps([f.serialize() for f in full_frames], indent=4))

    # write a summary results
    result = Result()
    result.pass_result = pass_result
    result.metrics.append(
        ResultMetric(
            name='time_collision_predicted',
            score=collision_predicted
        )
    )
    result.metrics.append(
        ResultMetric(
            name='time_collision_occured',
            score=collision_occurred
        )
    )
    set_result(result, results_path)


def main():
    """main"""
    args = parse_arguments()
    if args['cloud']:
        # just pass main UUT function to cloud loop
        loop(main_uut, verbose=True)
    else:
        # local test for development
        asset_dir = args['assets']
        scenario_file = 'scenario_collision.json' if args['collision'] else 'scenario.json'

        # create simulator
        simulator = Simulator.from_file(
            os.path.join(asset_dir, 'simulator.json'),
            trajectory=os.path.join(asset_dir, scenario_file),
            weather=os.path.join(asset_dir, 'weather.json'),
            ego=os.path.join(asset_dir, 'vehicle.json'),
            sensors=os.path.join(asset_dir, 'sensors.json')
        )

        # where to write results
        results_path = os.path.join(asset_dir, 'results.json')
        results_full_path = os.path.join(asset_dir, 'results_full.json')

        # run
        main_uut(simulator, results_path, results_full_path)


def parse_arguments():
    """helper function to parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--assets',
        help='Directory containing configuration files for simulator',
        default='config'
    )
    parser.add_argument(
        '-c', '--cloud',
        help='Indicates that we are running in the monoDrive cloud deployment',
        default=False, action='store_true'
    )
    parser.add_argument(
        '--collision',
        help='Flag to run collision version of NCAP scenario',
        default=False, action='store_true'
    )
    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    main()
