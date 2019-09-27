class ElasticIngestionDataValidationException(Exception):
    """ Base class for the elastic ingestion data validation """
    pass


class ElasticIngestionDataValidationInvalidDataStructureElement(ElasticIngestionDataValidationException):
    """ Raised when the data set does not match expectations of list of dictionaries """
    message = 'Invalid data structure: expecting list of dictionaries'


class ElasticIngestionDataValidationNoTimeElement(ElasticIngestionDataValidationException):
    """
    Raised when there is no time element in the first array of the data list. 

    This is important because ElasticSearch is currently using the first time element in
    the array to designate the unique ID for the run of that scenario.
    """
    message = 'No `time` key in first element'


class ElasticIngestionDataValidationNoGameTimeElement(ElasticIngestionDataValidationException):
    """
    Raised when there is no game_time element in the first array of the data list. 

    This is important because the @timestamp key that is sent to ElasticSearch is meant to reflect
    the time of ingestion (IE: datetime.now()) + game_time (In Millisecond Epoch) for each node in the
    report.
    """
    message = 'No `game_time` key in first element'


class NetworkAPIError(Exception):
    """ Base class for network api errors """
    def __init__(self, status, message):
        self.status = status
        self.message = message

class ElasticNetworkAPIError(NetworkAPIError):
    pass

class KibanaNetworkAPIError(NetworkAPIError):
    pass
