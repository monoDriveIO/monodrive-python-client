"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
import json
import os
import time
import signal

from monodrive.simulator import Simulator
from uut.vehicles.example_vehicle import ExampleVehicle
from monodrive import utils
from uut.ingestion import ElasticIngestion

from tests import BaseUnitTestHelper


class ReportingTrajectoryUnitTest(BaseUnitTestHelper):

    def setUp(self):
        # setup configuration
        self.file_instances = []
        self.trajectory = self.get_trajectory_file('AEB_20_0_CCRS_Collision.json')
        self.sim_config = self.get_configuration('simulator.json')
        self.weather_config = self.get_configuration('weather.json')
        self.running = True


        self.simulator = self.get_simulator(self.sim_config, self.trajectory, weather=self.weather_config)
        self.simulator.start()
        signal.signal(signal.SIGINT, self.stop_simulator)

    def tearDown(self):
        self.stop_simulator()
        # cleanup open buffers
        for f in self.file_instances:
            f.close()

    def stop_simulator(self):
        self.running = False
        self.simulator.stop()
        print("Stopping the simulator.")

    def get_json_file(self, json_file):
        f = open(os.path.join(self.base_path, json_file), 'r')
        self.file_instances.append(f)
        return json.load(f)

    def get_trajectory_file(self, trajectory_file):
        return self.get_json_file(os.path.join('configurations', 'trajectories', trajectory_file))

    def get_configuration(self, config_file):
        return self.get_json_file(os.path.join('configurations', config_file))

    def get_simulator(self, sim_config, trajectory, weather=None):
        simulator = Simulator(sim_config, trajectory)
        # Load and configure the weather conditions for the simulator
        if weather is not None:
            profile = weather['profiles'][10]
            profile['id'] = 'test'
            # TODO: Seems the weather config was never sent in the original file
        return simulator

    def test_sensor_config_file(self):
        # Load the sensor configuration and software under test
        sensor_config = json.load(open(os.path.join(self.base_path, 'uut', 'gps_config.json')))

        vehicle = ExampleVehicle(self.sim_config, sensor_config)
        vehicle.start()
        vehicle.initialize_perception()
        vehicle.initialize_reporting()
        print(vehicle.sensors_ids)

        # Start stepping the simulator
        for i in range(0, len(self.trajectory)-1):
            start_time = time.time()
            response = vehicle.step()
            # print("Step = {0} completed in {1:.2f}ms".format(i, ((time.time()-start_time)*1000), 2))
            #time.sleep(1)
            if self.running is False:
                break

        vehicle.generate_report_summary()
        vehicle.summary["Scenario"] = self.trajectory_file
        print("DATA: ",len(vehicle.full_report))
        report = ElasticIngestion()
        report.scenario = self.trajectory_file
        report.customer = "Dummy"
        report.data = vehicle.full_report
        report.generate_full_report()
        utils.send_summary_to_mongodb(vehicle.summary)
        
        print("Stopping the uut.")
        vehicle.stop()

