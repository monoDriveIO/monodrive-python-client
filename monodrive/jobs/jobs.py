"""
helpful utilities and functions for managing job assignments
in cloud deployment and desktop environment
"""

# lib
import os
import time
import enum
import json
import argparse
from typing import Callable
import objectfactory

# src
from monodrive.simulator import Simulator

# constants
ASSET_DIR = './mdassets'
STATE_FILE = 'STATUS'
SIMULATOR_FILE = 'simulator.json'
SCENARIO_FILE = 'scenario.json'
WEATHER_FILE = 'weather.json'
VEHICLE_FILE = 'vehicle.json'
SENSORS_FILE = 'sensors.json'
RESULTS_FILE = 'results.json'
REPORT_FILE = 'results_full.json'

POLL_INTERVAL = 3

ASSET_DIR_FLAG = 'md_assets'
SIMULATOR_FLAG = 'md_simulator'
SCENARIO_FLAG = 'md_scenario'
WEATHER_FLAG = 'md_weather'
VEHICLE_FLAG = 'md_vehicle'
SENSORS_FLAG = 'md_sensors'
RESULTS_FLAG = 'md_results'
LOOP_FLAG = 'md_loop'


class JobState(enum.Enum):
    """
    enum for allowable job micro states during processing
    """
    ASSIGNED = 0
    CONFIGURING = 1
    READY = 2
    RUNNING = 3
    FINISHING = 4
    COMPLETED = 5
    FAILED = 6


@objectfactory.Factory.register_class
class ResultMetric(objectfactory.Serializable):
    """data model for single result metric"""
    name = objectfactory.Field()
    score = objectfactory.Field()


@objectfactory.Factory.register_class
class Result(objectfactory.Serializable):
    """data model for results of UUT run"""
    pass_result = objectfactory.Field(name='pass')
    metrics = objectfactory.List(field_type=ResultMetric)
    message = objectfactory.Field()


def set_result(result: Result, path: str = None):
    """
    helper to set the result of UUT run

    Args:
        result: results data model
        path: results path
    """
    if path is None:
        args = parse_md_arguments()
        if args[ASSET_DIR_FLAG]:
            path = os.path.join(args[ASSET_DIR_FLAG], RESULTS_FILE)
        if args[RESULTS_FLAG]:
            path = args[RESULTS_FLAG]
    if path is None:
        raise ValueError('no results path provided')
    with open(path, 'w') as file:
        json.dump(result.serialize(), file, indent=4)


def get_state() -> JobState:
    """
    helper to get job state

    Returns:
        enumerated JobState
    """
    state_path = get_state_path()
    if not os.path.exists(state_path):
        raise ValueError('path does not exist: {}'.format(state_path))
    with open(os.path.join(ASSET_DIR, STATE_FILE), 'r') as file:
        text_name = file.read()
    try:
        state = JobState[text_name]
    except KeyError as e:
        raise ValueError('Invalid state: {}'.format(e))
    return state


def set_state(state: JobState):
    """
    helper to set jobs job state

    Args:
        state: enumerated jobs job state
    """
    state_path = get_state_path()
    with open(state_path, 'w') as file:
        file.write(state.name)


def get_state_path() -> str:
    """
    helper function to infer state file path from command line args

    Returns:
        str: path
    """
    args = parse_md_arguments()

    if args[ASSET_DIR_FLAG] is None:
        raise ValueError('no assets directory provided to locate state file')

    return os.path.join(args[ASSET_DIR_FLAG], STATE_FILE)


def get_simulator(verbose: bool = False):
    """
    helper factory function to create a simulator object based on
    command line arguments

    Args:
        verbose:

    Returns:
        Simulator
    """
    args = parse_md_arguments()

    config_path = None
    scenario_path = None
    weather_path = None
    sensors_path = None

    # set paths from assets directory if provided
    if args[ASSET_DIR_FLAG]:
        config_path = os.path.join(args[ASSET_DIR_FLAG], SIMULATOR_FILE)
        scenario_path = os.path.join(args[ASSET_DIR_FLAG], SCENARIO_FILE)
        weather_path = os.path.join(args[ASSET_DIR_FLAG], WEATHER_FILE)
        sensors_path = os.path.join(args[ASSET_DIR_FLAG], SENSORS_FILE)

    # set/update with individual flags
    if args[SIMULATOR_FLAG]:
        config_path = args[SIMULATOR_FLAG]
    if args[SCENARIO_FLAG]:
        scenario_path = args[SCENARIO_FLAG]
    if args[WEATHER_FLAG]:
        weather_path = args[WEATHER_FLAG]
    if args[SENSORS_FLAG]:
        sensors_path = args[SENSORS_FLAG]

    if config_path is None:
        raise ValueError('no simulator config path provided')

    # create simulator
    simulator = Simulator.from_file(
        config_path,
        scenario=scenario_path,
        weather=weather_path,
        sensors=sensors_path,
        verbose=verbose
    )
    return simulator


def run_job(uut_main: Callable[[], None], verbose: bool = False):
    """
    main entry point to run a monodrive job

    supports single-run development, local batch runner, and cloud deployment

    Args:
        uut_main:
        verbose:
    """
    args = parse_md_arguments()

    if not args[LOOP_FLAG]:
        uut_main()

    while 1:
        if verbose:
            print('Starting monoDrive job loop')

        # wait until ready
        while 1:
            time.sleep(POLL_INTERVAL)
            try:
                state = get_state()
            except ValueError as e:
                if verbose:
                    print('State file could not be parsed: {}'.format(e))
                continue
            if verbose:
                print('Status: {}'.format(state))
            if state == JobState.READY:
                break

        # run uut
        try:
            uut_main()
        except Exception as e:
            print('Error in UUT main: {}'.format(e))
            set_state(JobState.FAILED)
            if verbose:
                print('Set job state: {}'.format(JobState.FAILED))
            continue

        # set done
        set_state(JobState.COMPLETED)
        if verbose:
            print('Set job state: {}'.format(JobState.COMPLETED))


def parse_md_arguments():
    """internal command line parser for monodrive job arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--{}'.format(ASSET_DIR_FLAG), required=False)
    parser.add_argument('--{}'.format(SIMULATOR_FLAG), required=False)
    parser.add_argument('--{}'.format(SCENARIO_FLAG), required=False)
    parser.add_argument('--{}'.format(WEATHER_FLAG), required=False)
    parser.add_argument('--{}'.format(VEHICLE_FLAG), required=False)
    parser.add_argument('--{}'.format(SENSORS_FLAG), required=False)
    parser.add_argument('--{}'.format(RESULTS_FLAG), required=False)
    parser.add_argument('--{}'.format(LOOP_FLAG), required=False, action='store_true')
    args = vars(parser.parse_known_args()[0])
    return args
