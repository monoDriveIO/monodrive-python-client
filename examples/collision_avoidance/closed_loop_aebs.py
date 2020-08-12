"""
Simple collision avoidance system being tested against the monodrive simulator
in closed loop mode
"""

# lib
import time
import threading
import argparse
from monodrive.sensors import *
from monodrive.jobs import run_job, get_simulator, set_result, Result, ResultMetric

# constants
AEBS_DIST_MAX = 400.0  # start applying brakes
AEBS_DIST_MIN = 50.0  # max brakes
TIMEOUT = 10

# global
lock = threading.RLock()
collision_occurred = None
collision_predicted = None
target_distance = None
processing = 0


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
    if nearest and nearest < AEBS_DIST_MAX:
        global collision_predicted, target_distance
        target_distance = nearest
        if collision_predicted is None:
            collision_predicted = frame.game_time
            print('Collision predicted, distance: {}, game time: {}'.format(
                nearest, frame.game_time
            ))

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

    # done processing
    with lock:
        global processing
        processing -= 1


def emergency_braking(distance: float, throttle: float) -> (float, float, float, int):
    """
    Function to process target distance and update controls for collision avoidance

    Args:
        distance:
        throttle:

    Returns:
        control commands as tuple
    """
    if distance > AEBS_DIST_MAX:
        return throttle, 0.0, 0.0, 1
    distance = max(distance, AEBS_DIST_MIN)  # okay if lower

    brake = (AEBS_DIST_MAX - distance) / (AEBS_DIST_MAX - AEBS_DIST_MIN)

    return 0.0, 0.0, brake, 1


def main():
    """main uut driver function"""
    args = parse_arguments()

    # setup globals
    global collision_occurred, collision_predicted, target_distance
    collision_occurred = None
    collision_predicted = None
    target_distance = None

    # create simulator object
    simulator = get_simulator(verbose=args['verbose'])
    simulator.map = 'Straightaway5k'
    simulator.mode = 0

    # start simulator and subscribe to sensors
    res = simulator.start()
    simulator.subscribe_to_sensor('Collision_8800', collision_on_update)
    simulator.subscribe_to_sensor('Ultrasonic_8300', ultrasonic_on_update)

    # UUT code
    time_start = time.time()
    while 1:

        # expect 2 sensors to be processed
        with lock:
            global processing
            processing = 2

        # get controls
        if collision_predicted and target_distance:
            controls = emergency_braking(target_distance, args['throttle'])
            if args['verbose']:
                print(controls)
        else:
            controls = (args['throttle'], 0, 0, 1)

        # apply control and sample sensors
        res = simulator.send_control(*controls)
        res = simulator.sample_sensors()

        # wait for processing to complete
        while True:
            with lock:
                if processing == 0:
                    break
            time.sleep(0.05)

        if collision_occurred:
            print('Collision occurred - exiting early.')
            break

        if time.time() - time_start > TIMEOUT:
            break

    simulator.stop()

    # pass/fail criteria
    pass_result = True
    if collision_occurred:
        pass_result = False
    # TODO - max deceleration

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
        '-v', '--verbose',
        help='Do verbose logging',
        default=False, action='store_true'
    )
    parser.add_argument(
        '-t', '--throttle',
        help='Value for throttle (0-1)',
        type=float, default=0.5
    )
    args = vars(parser.parse_known_args()[0])
    return args


if __name__ == '__main__':
    run_job(main, verbose=True)
