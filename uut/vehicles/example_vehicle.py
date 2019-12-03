
from monodrive.base_vehicle import BaseVehicle
from uut.perception import Perception
from uut.reporting import Reporting


class ExampleVehicle(BaseVehicle):
    def __init__(self, config, sensors):
        super().__init__(config, sensors)
        self.perception = None
        self.reporting = Reporting(self.sensors_ids)

    def initialize_perception(self):
        self.perception = Perception(self.sensors_ids)
        self.subscribe_to_sensor("Camera_8000", self.perception.on_update)

    def initialize_reporting(self):
        self.subscribe_to_sensor("Collision_8800", self.reporting.on_update)
