import json
import base64
from urllib import request, parse, error

from uut.ingestion.exceptions import ElasticNetworkAPIError, KibanaNetworkAPIError
from uut.ingestion.settings import (ELASTIC_URL, ELASTIC_USER, ELASTIC_PASS,
                                    KIBANA_URL, KIBANA_USER, KIBANA_PASS)


class NetworkResponse(object):
    """
    A simple response object that stores if the original request was for JSON or not.
    """
    def __init__(self, status, body, is_json=False):
        self.status = status
        self.body = body
        self.is_json = is_json

    @property
    def json(self):
        if not self.is_json:
            raise AttributeError('Response is not flagged as json; use self.body')
        return json.loads(self.body.decode())


class BaseNetwork(object):
    """
    A simple wrapper around urllib.request.Request to support a python-requests style API
    """
    USER = None
    PASSWORD = None
    API_ROOT = None

    def __init__(self):
        self.headers = {}
        if self.USER is None or self.PASSWORD is None or self.API_ROOT is None:
            raise NotImplementedError('USER, PASSWORD AND API_ROOT must not be None')

    def set_header(self, key, value):
        self.headers[key] = value

    def set_credentials(self):
        credentials = ('{0}:{1}'.format(self.USER, self.PASSWORD))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        self.set_header('Authorization', 'Basic {0}'.format(encoded_credentials.decode('ascii')))
        return encoded_credentials

    def build_url(self, action, query_string=None):
        url = '{0}{1}'.format(self.API_ROOT, action)
        if query_string is not None:
            return '{0}?{1}'.format(url, query_string)
        return url

    def request(self, method, action, data, json_request=False, headers={}):
        if len(headers):
            self.headers = headers

        self.set_credentials()
        if json_request:
            self.set_header('Content-Type', 'application/json')
        
        if method.lower() in ['get', 'options', 'delete', 'head']:
            url = self.build_url(action, query_string=data)
            req = request.Request(url,
                headers=self.headers, method=method)
        elif method.lower() in ['post', 'put', 'update']:
            url = self.build_url(action)
            req = request.Request(url,
                data=data, headers=self.headers, method=method)
        else:
            raise NotImplementedError('The method {0} is invalid'.format(method))

        try:
            resp = request.urlopen(req)
        except error.HTTPError as e:
            raise self.API_EXCEPTION_CLASS(
                'Failed: {0}'.format(e.readlines()))

        resp_data = resp.read()
        if resp.status != 200:
            raise self.API_EXCEPTION_CLASS(
                'Failed: {0} -> {1}'.format(resp.status, resp_data))

        return NetworkResponse(resp.status, resp_data, is_json=json_request)

    def _get(self, action, query_string_obj={}, json_request=False, headers={}):
        query_pairs = [(k,v) for k,vlist in query_string_obj.items() for v in vlist]
        query_string  = parse.urlencode(query_pairs)
        return self.request('GET', action, query_string, json_request=json_request, headers=headers)

    def _post(self, action, data, json_request=False, headers={}):
        return self.request('POST', action, data, json_request=json_request, headers=headers)

    @classmethod
    def get(cls, action, query_string_obj={}, headers={}):
        _inst = cls()
        return _inst._get(action, query_string_obj=query_string_obj, headers=headers)

    @classmethod
    def get_json(cls, action, query_string_obj={}, headers={}):
        _inst = cls()
        return _inst._get(action, query_string_obj=query_string_obj, json_request=True, headers=headers)

    @classmethod
    def post(cls, action, data, headers={}):
        _inst = cls()
        return _inst._post(action, data, headers=headers)

    @classmethod
    def post_json(cls, action, data, headers={}):
        _inst = cls()
        return _inst._post(action, data, json_request=True, headers=headers)


class ElasticNetwork(BaseNetwork):
    USER = ELASTIC_USER
    PASSWORD = ELASTIC_PASS
    API_ROOT = ELASTIC_URL
    API_EXCEPTION_CLASS = ElasticNetworkAPIError


class KibanaNetwork(BaseNetwork):
    USER = KIBANA_USER
    PASSWORD = KIBANA_PASS
    API_ROOT = KIBANA_URL
    API_EXCEPTION_CLASS = KibanaNetworkAPIError