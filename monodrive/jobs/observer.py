"""
observers for monitoring and reporting of simulation jobs
in cloud deployment and desktop environment
"""

# lib
import objectfactory
from elasticsearch import Elasticsearch

# src
from monodrive.sensors import DataFrame, CollisionFrame, IMUFrame

# constants
ELASTIC_INDEX = 'jobs'


class Observer(objectfactory.Serializable):
    """
    base class for job observer
    """

    def configure(self, job: str, batch: str, host: str, port: str):
        """
        configure job observer

        Args:
            job: job id
            batch: batch id
            host: elastic search host
            port: elastic search port
        """
        self.job_id = job
        self.batch_id = batch
        self.elastic = Elasticsearch(['{}:{}'.format(host, port)])

    def callback(self, frame: DataFrame):
        raise NotImplementedError('observer callback() method must be implemented')

    def sensor(self) -> dict:
        raise NotImplementedError('oberver sensor() generator must be implemented')


@objectfactory.Factory.register_class
class CollisionObserver(Observer):
    """
    observer to monitor for collision of vehicle with other actors
    """

    def callback(self, frame: CollisionFrame):
        """
        parse sensor dataframe and post observer message to elastic

        Args:
            dataframe: collision sensor dataframe

        Returns:
            none
        """
        doc = {
            'job_id': self.job_id,
            'batch_id': self.batch_id,
            'timestamp': frame.timestamp,
            'game_time': frame.game_time,
            'observer': 'collision',
            'name': 'distance',
            'value': frame.distance
        }

        res = self.elastic.index(index=ELASTIC_INDEX, body=doc)

    def sensor(self) -> dict:
        """
        create collision sensor config to be used for observer

        Returns:
            collision sensor config as dict
        """
        return {
            "type": "Collision",
            "listen_port": 8881,
            "desired_tags": ["vehicle"],
            "undesired_tags": ["static"]
        }


@objectfactory.Factory.register_class
class AccelerationObserver(Observer):
    """
    observer to monitor acceleration of ego vehicle
    """

    def callback(self, frame: IMUFrame):
        """
        parse sensor dataframe and post observer message to elastic

        Args:
            dataframe: IMU sensor dataframe

        Returns:
            none
        """
        doc = {
            'job_id': self.job_id,
            'batch_id': self.batch_id,
            'timestamp': frame.timestamp,
            'game_time': frame.game_time,
            'observer': 'acceleration',
            'name': 'x',
            'value': frame.acceleration_vector[0]
        }
        res = self.elastic.index(index=ELASTIC_INDEX, body=doc)

        doc = {
            'job_id': self.job_id,
            'batch_id': self.batch_id,
            'timestamp': frame.timestamp,
            'game_time': frame.game_time,
            'observer': 'acceleration',
            'name': 'y',
            'value': frame.acceleration_vector[1]
        }
        res = self.elastic.index(index=ELASTIC_INDEX, body=doc)

        doc = {
            'job_id': self.job_id,
            'batch_id': self.batch_id,
            'timestamp': frame.timestamp,
            'game_time': frame.game_time,
            'observer': 'acceleration',
            'name': 'z',
            'value': frame.acceleration_vector[2]
        }
        res = self.elastic.index(index=ELASTIC_INDEX, body=doc)

    def sensor(self) -> dict:
        """
        create IMU sensor config to be used for observer

        Returns:
            IMU sensor config as dict
        """
        return {
            "type": "IMU",
            "listen_port": 8882
        }
