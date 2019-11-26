import json
import os
from monodrive.simulator import Simulator
from uut.client import UUT_Client
import monodrive.messaging as mmsg
from uut.base_sensor import Sensor
import signal

class MatlabVehicle():
    def __init__(self):
        self.a = 1
        self.root = os.path.dirname(__file__)
        # Load the trajectory and simulator configurations
        self.trajectory = json.load(open(os.path.join(self.root, 'configurations', 'trajectories', 'HighWayExitReplay.json')))
        self.sim_config = json.load(open(os.path.join(self.root, 'configurations', 'simulator.json')))

        # configure this simulator client
        # Load the reporting sensor configuration and software under test
        # reporting_config = json.load(open(os.path.join(root, 'monodrive', 'reporting_config.json')))
        self.simulator = Simulator(self.sim_config, self.trajectory)
        # Load the sensor configuration and software under test
        self.sensor_config = json.load(open(os.path.join(self.root, 'uut', 'gps_config.json')))
        #self.__client = UUT_Client(self.sim_config['server_ip'], self.sim_config['server_port'])
        #self.__client.connect()
        self.client = self.simulator.client
        self.__running = True
        self.__sensors = dict()


    def start_simulator(self):
        # Start the simulation
        self.simulator.start()

    def send_sensor_configuration(self):
        """Configure the server with the current simulator settings"""
        self.send_command(mmsg.ApiMessage(
            mmsg.ID_REPLAY_CONFIGURE_SENSORS_COMMAND, self.sensor_config))

    def start_sensor_listening(self):
        """Start all sensors"""
        self.__running = True
        for sc in self.sensor_config:
            sensor = Sensor(self.sim_config['server_ip'], sc)
            sensor.start()
            self.__sensors[sensor.id] = sensor

    def stop(self):
        """Stop the simulation and all attached sensors."""
        #self.client.disconnect()
        for sensor_id in self.__sensors.keys():
            self.__sensors[sensor_id].stop()
        self.__running = False

    def step(self, steps=1):
        """Step the simulation the specified number of steps.

        Args:
            steps(int): The number of steps to move the simulation

        Raises:
            Exception if the simulator is not currently running
        """
        if not self.__running:
            raise Exception("Simulator is not running")

        response = self.send_command(
            mmsg.ApiMessage(mmsg.ID_REPLAY_STEP_SIMULATION_COMMAND,
                            {
                                u'amount': steps
                            }))
        return response


    def send_control(self, forward, right):
        self.send_command(
            mmsg.ApiMessage(mmsg.ID_EGO_CONTROL,
                            {
                                u'forward_amount': forward,
                                u'right_amount': right,
                                u'brake_amount': 0,
                                u'drive_mode': 1
                            }))


    def send_command(self, command):
        """Send the command to the connected simulator client.

        Args:
            command(ApiMessage): The command to send to the server.
        """
        command.write(self.client)
        return command.read(self.client)

if __name__ == '__main__':
    def handler(signum, frame):
        """"Signal handler to turn off the simulator with ctl+c"""
        global running
        running = False

    signal.signal(signal.SIGINT, handler)
    v = MatlabVehicle()
    v.start_simulator()
    v.send_sensor_configuration()
    v.start_sensor_listening()
    for n in range(0, 10, 1):
        print("step")
        v.step(1)
    v.stop()