"""
helpful utilities and functions for managing job assignments
in cloud deployment and desktop environment
"""

# lib
import os
import time
import enum
import json
from typing import Callable
import objectfactory

# src
from monodrive.simulator import Simulator

# constants
ASSET_DIR = '/mdassets'
STATE_FILE = 'STATUS'
POLL_INTERVAL = 3
SIMULATOR_FILE = 'simulator.json'
SCENARIO_FILE = 'scenario.json'
WEATHER_FILE = 'weather.json'
VEHICLE_FILE = 'vehicle.json'
SENSORS_FILE = 'sensors.json'
RESULTS_FILE = 'results.json'
REPORT_FILE = 'results_full.json'


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


def set_result(result: Result, path: str):
    """
    helper to set the result of UUT run

    Args:
        result: results data model
        path: results path
    """
    with open(path, 'w') as file:
        json.dump(result.serialize(), file, indent=4)


def get_state() -> JobState:
    """
    helper to get job state

    Returns:
        enumerated JobState
    """
    if not os.path.exists(os.path.join(ASSET_DIR, STATE_FILE)):
        return None
    with open(os.path.join(ASSET_DIR, STATE_FILE), 'r') as file:
        text_name = file.read()
    try:
        state = JobState[text_name]
    except KeyError as e:
        print('Invalid state: {}'.format(e))
        return None
    return state


def set_state(state: JobState):
    """
    helper to set jobs job state

    Args:
        state: enumerated jobs job state
    """
    with open(os.path.join(ASSET_DIR, STATE_FILE), 'w') as file:
        file.write(state.name)


def loop(
        uut_main: Callable[[Simulator, str, str], None],
        verbose=False
):
    """
    Main driver loop to enable execution of multiple UUT jobs on single node

    Returns:

    """
    while 1:
        if verbose:
            print('Starting monoDrive job loop')

        # wait until ready
        while 1:
            time.sleep(POLL_INTERVAL)
            state = get_state()
            if state is None:
                if verbose:
                    print('State file could not be parsed')
                continue
            if verbose:
                print('Status: {}'.format(state))
            if state == JobState.READY:
                break

        # create simulator
        simulator = Simulator.from_file(
            os.path.join(ASSET_DIR, SIMULATOR_FILE),
            trajectory=os.path.join(ASSET_DIR, SCENARIO_FILE),
            weather=os.path.join(ASSET_DIR, WEATHER_FILE),
            ego=os.path.join(ASSET_DIR, VEHICLE_FILE),
            sensors=os.path.join(ASSET_DIR, SENSORS_FILE),
            verbose=verbose
        )

        # where to write results
        results_path = os.path.join(ASSET_DIR, RESULTS_FILE)
        results_full_path = os.path.join(ASSET_DIR, REPORT_FILE)

        # run uut
        try:
            uut_main(simulator, results_path, results_full_path)
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
