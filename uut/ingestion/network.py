import json
import base64
import uuid
import io
import mimetypes
import requests
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
        return json.load(self.body)


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

    def _data_prep(self, data):
        return json.dumps(data).encode()

    def _data_prep_form_post(self, data):
        form = MultiPartForm()
        form.add_file('file', 'file.ndjson', data)
        form_buffer =  form.get_binary().getvalue()
        self.set_header('Content-type', form.get_content_type())
        self.set_header('Content-length', str(len(form_buffer)))
        return form_buffer

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

    def form_post(self, url, data):
        #data = self._data_prep_form_post(data)
        resp = requests.post(url, files={'file':('file.ndjson',data.read())}, headers=self.headers)
        return NetworkResponse(resp.status_code, resp.text, is_json=False)

    def request(self, method, action, data, json_request=False, form_request=False, headers={}):
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
            if form_request:
                return self.form_post(url, data)

            if json_request:
                data = self._data_prep(data)

            req = request.Request(url,
                data=data, headers=self.headers, method=method)
        else:
            raise NotImplementedError('The method {0} is invalid'.format(method))

        try:
            resp = request.urlopen(req)
        except error.HTTPError as e:
            raise self.API_EXCEPTION_CLASS(e.status,
                'Failed: {0}'.format(e.readlines()))
        except TypeError as e:
            raise self.API_EXCEPTION_CLASS(500,
                'Make sure your data is JSON encoded.')

        if resp.status != 200:
            raise self.API_EXCEPTION_CLASS(resp.status,
                'Failed: {0} -> {1}'.format(resp.status, resp.read()))
        return NetworkResponse(resp.status, resp, is_json=json_request)

    def _get(self, action, query_string_obj={}, json_request=False, headers={}):
        query_pairs = [(k,v) for k,vlist in query_string_obj.items() for v in vlist]
        query_string  = parse.urlencode(query_pairs)
        return self.request('GET', action, query_string, json_request=json_request, headers=headers)

    def _post(self, action, data, json_request=False, form_request=False, headers={}):
        return self.request('POST', action, data, json_request=json_request, form_request=form_request, headers=headers)

    def _put(self, action, data, json_request=False, headers={}):
        return self.request('PUT', action, data, json_request=json_request, headers=headers)

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

    @classmethod
    def put(cls, action, data, headers={}):
        _inst = cls()
        return _inst._put(action, data, headers=headers)

    @classmethod
    def put_json(cls, action, data, headers={}):
        _inst = cls()
        return _inst._put(action, data, json_request=True, headers=headers)

    @classmethod
    def formpost(cls, action, data, headers={}):
        _inst = cls()
        return _inst._post(action, data, form_request=True, headers=headers)


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


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = uuid.uuid4().hex.encode('utf-8')
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary.decode()

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return

    def get_binary(self):
        """Return a binary buffer containing the form data, including attached files."""
        part_boundary = '--{0}--'.format(self.boundary.decode())

        binary = io.BytesIO()
        needsCLRF = False
        # Add the form fields
        for name, value in self.form_fields:
            if needsCLRF:
                binary.write('\r\n'.encode())
            needsCLRF = True

            block = [part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value
            ]
            binary.write('\r\n'.join(block))

        # Add the files to upload
        for field_name, filename, content_type, body in self.files:
            if needsCLRF:
                binary.write('\r\n'.encode())
            needsCLRF = True

            block = [part_boundary,
              str('Content-Disposition: file; name="%s"; filename="%s"' % \
              (field_name, filename)),
              'Content-Type: %s' % content_type,
              ''
              ]
            binary.write('\r\n'.join(block).encode())
            binary.write('\r\n'.encode())
            binary.write(body)


        # add closing boundary marker,
        binary.write('\r\n--{0}--\r\n'.format(self.boundary.decode()).encode())
        return binary