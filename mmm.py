import json
import os
import time
import signal
import monodrive.messaging as mmsg
from uut.client import UUT_Client
from monodrive.simulator import Simulator
#from uut.vehicles.example_vehicle import ExampleVehicle

def test_func():
    root = os.path.dirname(__file__)

    # Flag to allow user to stop the simulation from SIGINT
    running = True


    def handler(signum, frame):
        """"Signal handler to turn off the simulator with ctl+c"""
        global running
        running = False


    signal.signal(signal.SIGINT, handler)

    # Load the trajectory and simulator configurations
    trajectory = json.load(open(os.path.join(root, 'configurations', 'trajectories', 'HighWayExitReplay.json')))
    sim_config = json.load(open(os.path.join(root, 'configurations', 'simulator.json')))

    # configure this simulator client
    # Load the reporting sensor configuration and software under test
    # reporting_config = json.load(open(os.path.join(root, 'monodrive', 'reporting_config.json')))
    simulator = Simulator(sim_config, trajectory)

    # Load and configure the weather conditions for the simulator
    weather = json.load(
        open(os.path.join(root, 'configurations', 'weather.json')))
    profile = weather['profiles'][10]
    profile['id'] = 'test'

    # Start the simulation
    simulator.start()

    # Load the sensor configuration and software under test
    sensor_config = json.load(open(os.path.join(root, 'uut', 'gps_config.json')))
    sensor_msg = mmsg.ApiMessage(mmsg.ID_REPLAY_CONFIGURE_SENSORS_COMMAND, sensor_config)
    client = UUT_Client(sim_config['server_ip'], sim_config['server_port'])
    client.connect()
    success = sensor_msg.write(client)
    return success

if __name__ == '__main__':
    test_func()