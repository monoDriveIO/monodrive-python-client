from .client import Client
from .messaging import ApiMessage, REPLAY_ConfigureSensorsCommand_ID, REPLAY_ConfigureTrajectoryCommand_ID, \
    REPLAY_StepSimulationCommand_ID, SimulatorConfig_ID, WeatherConfigCommand_ID
from .sensors import Sensor
import signal


ClosedLoop = 0
Replay = 1
PXI = 2

class Simulator:

    def __init__(self, config, sensors, trajectory):
        self.config = config
        self.sensor_config = sensors
        self.sensors = []
        self.trajectory = trajectory
        self.client = Client(config['server_ip'], config['server_port'])
        self.client.connect()
        self.is_running = False

    def set_mode(self, mode):
        self.config['simulation_mode'] = mode

    def set_weather(self, weather):
        return self.configure_weather({
                                 u"set_profile": weather
                             })

    def configure_weather(self, config):
        message = ApiMessage(WeatherConfigCommand_ID,
                             config)
        message.write(self.client)
        return message.read(self.client)

    def configure(self):
        self._send_command(ApiMessage(SimulatorConfig_ID, self.config))
        self._send_command(ApiMessage(REPLAY_ConfigureSensorsCommand_ID, self.sensor_config))
        self._send_command(ApiMessage(REPLAY_ConfigureTrajectoryCommand_ID, self.trajectory))

    def start(self):
        signal.signal(signal.SIGINT, self._sig_int_handler)
        signal.signal(signal.SIGTERM, self._sig_int_handler)
        self.is_running = True
        self.configure()

        for sc in self.sensor_config:
            if sc['sensor_process']:
                sensor = Sensor(self.config['server_ip'], sc)
                sensor.source.subscribe(lambda data: print("{0}: data frame ({1}, {2}, {3})".format(
                    sensor.id, data[0], data[1], len(data[2]))))
                sensor.start()
                self.sensors.append(sensor)

    def stop(self):
        for sensor in self.sensors:
            sensor.stop()
        self.is_running = False

    def step(self, steps=1):
        if not self.is_running:
            raise Exception("simulator is not running")

        self._send_command(ApiMessage(REPLAY_StepSimulationCommand_ID,
                                      {
                                          u'amount': steps
                                      }))

    def _send_command(self, command):
        print(command)
        command.write(self.client)
        print(command.read(self.client))

    def _sig_int_handler(self, signum, frame):
        self.stop()
