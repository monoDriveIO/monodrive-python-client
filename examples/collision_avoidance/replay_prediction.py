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
from monodrive.sensors import *
from monodrive.jobs import run_job, get_simulator, set_result, Result, ResultMetric

# constants
PREDICT_WINDOW_MIN = 0.01  # 10ms
PREDICT_WINDOW_MAX = 1.0  # 1s

# global
lock = threading.RLock()
collision_occurred = None
collision_predicted = None
prediction_threshold = 200
processing = 0
full_frames = []


def ultrasonic_on_update(frame: UltrasonicFrame):
    """
    Callback to process a parsed Ultrasonic frame

    Attempt to predict when a collision will occur based on 3d point cloud
    information parsed from the Ultrasonic data

    Args:
        frame: parsed Ultrasonic frame
    """
    # compute nearest point
    ranges = [t.range for t in frame.targets if t.range != -1.0]
    nearest = None
    if ranges:
        nearest = min(ranges)

    # predict
    global prediction_threshold
    if nearest and nearest < prediction_threshold:
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


def main():
    """main uut driver function"""
    args = parse_arguments()

    # setup globals
    global collision_occurred, collision_predicted, prediction_threshold
    collision_occurred = None
    collision_predicted = None
    prediction_threshold = args['distance']

    # create simulator object
    simulator = get_simulator(args['verbose'])
    simulator.map = 'Straightaway5k'
    simulator.mode = 2

    # start simulator and subscribe to sensors
    res = simulator.start()
    simulator.subscribe_to_sensor('Collision_8800', collision_on_update)
    simulator.subscribe_to_sensor('Ultrasonic_8300', ultrasonic_on_update)

    # UUT code
    for n in range(simulator.num_steps):
        if args['verbose']:
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
            name='time_collision_occurred',
            score=collision_occurred
        )
    )
    set_result(result)


def parse_arguments():
    """helper function to parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--distance',
        help='Distance at which to trigger collision prediction',
        type=float, default=200
    )
    parser.add_argument(
        '-v', '--verbose',
        help='Do verbose logging',
        default=False, action='store_true'
    )
    args = vars(parser.parse_known_args()[0])
    return args


if __name__ == '__main__':
    run_job(main, verbose=True)
