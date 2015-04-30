"""
Client class and exception for performing basic REST API interactions.

"""
from __future__ import print_function

__author__ = 'Andrew Gillis'

import json
import base64
import os
import sys

try:
    from urllib.parse import quote, unquote, urlencode
    from http.client import HTTPConnection
except ImportError:
    from urllib import quote, unquote, urlencode
    from httplib import HTTPConnection


class RestHttpError(Exception):

    """
    Exception object returned when REST API error occurs.

    """

    def __init__(self, http_status, code, msg):
        self.code = int(code)
        self.http_status = int(http_status)
        self.msg = msg

    def __int__(self):
        """Get HTTP status code."""
        return self.http_status

    def __str__(self):
        """Get error message."""
        return self.msg

    def code(self):
        """Get REST API error code."""
        return self.code


class RestHttp(object):

    """
    REST API client wrapper object base class.

    Derive application-specific REST API class from this base class.

    """

    def __init__(self, server, port=80, uri_base=None, user=None,
                 password=None, debug_print=False):
        """Initialize the REST API wrapper object.

        Arguments:
        server      -- STC REST API server to connect to. None to use environ.
        port        -- HTTP port to connect to server on.  Default is 80.
        uri_base    -- Part of URI that always follows http://server/
        user        --
        password    --
        debug_print -- Enable debug print statements.

        """
        self._server = server
        port = int(port)
        if port < 1 or port > 65535:
            raise ValueError('invalid port value')
        self._port = port
        self._base_headers = {'Accept': 'application/json'}
        self._uri_base = uri_base if uri_base else ''
        self._user = user
        self._password = password
        self._dbg_print = debug_print

        # autheticated API
        if user and password:
            b64string = base64.encodestring('%s:%s' % (user, password))[:-1]
            self._base_headers["Authorization"] = "Basic %s" % b64string

    def base_url(self):
        return self._uri_base

    def resource_to_url(self, resource):
        return '%s/%s' % (self._uri_base, quote(resource))

    def url_to_resource(self, uri):
        resource = uri.split(self._uri_base, 1)[-1].strip('/')
        return unquote(resource.split('/', 1)[-1])

    def make_uri(self, container, resource=None, query_items=None):
        pth = [self._uri_base]
        if container:
            pth.append(container)
        resource = '' if resource is None else quote(resource)
        if query_items:
            resource += RestHttp._get_query_str(query_items)
        pth.append(resource)
        return '/'.join(pth)

    ###########################################################################
    # protected methods
    #
    def _get_request(self, container, resource=None, query_items=None,
                     accept=None):
        uri = self.make_uri(container, resource, query_items)
        return self.__transact_http('GET', uri, None, accept)

    def _post_request(self, container, resource=None, params=None,
                      accept=None):
        uri = self.make_uri(container, resource, None)
        return self.__transact_http('POST', uri, params, accept)

    def _put_request(self, container, resource=None, params=None, accept=None):
        uri = self.make_uri(container, resource, None)
        return self.__transact_http('PUT', uri, params, accept)

    def _delete_request(self, container, resource, accept=None):
        uri = self.make_uri(container, resource, None)
        return self.__transact_http('DELETE', uri, None, accept)

    def _download(self, container, resource, query_items=None, accept=None):
        uri = self.make_uri(container, resource, None)
        headers = dict(self._base_headers)
        if accept:
            headers['Accept'] = accept
        if self._dbg_print:
            print('===> GET %s' % (uri,))

        conn = HTTPConnection(self._server, self._port)
        conn.connect()
        conn.request('GET', uri, None, headers)
        rsp = conn.getresponse()

        status = rsp.status
        data = None
        if status != 204:
            if self._dbg_print:
                print('===> response content-type:',
                      rsp.getheader('content-type'))
            data = rsp.read()
        conn.close()
        if status >= 300:
            raise RestHttpError(status, -1, str(data))

        return status, data

    @staticmethod
    def _get_query_str(items):
        return '?' + '&'.join((quote(i) for i in items))

    def _upload_multipart(self, resource, file_path, dst_name=None,
                          fields=None):
        if not os.path.exists(file_path):
            raise RuntimeError('file not found: ' + file_path)
        if not dst_name:
            dst_name = os.path.basename(file_path)
        headers = dict(self._base_headers)
        method = 'POST'
        content_type, body = self.__encode_multipart(file_path, dst_name,
                                                     fields)

        headers["content-type"] = content_type
        headers["content-length"] = str(len(body))
        uri = '%s/%s' % (self._uri_base, resource)
        if self._dbg_print:
            print('===> %s %s' % (method, uri))

        return self.__upload_http(method, headers, uri, body)


    def _upload(self, container, src_file_path, dst_name=None, put=True):
        if not os.path.exists(src_file_path):
            raise RuntimeError('file not found: ' + src_file_path)
        if not dst_name:
            dst_name = os.path.basename(src_file_path)
        headers = dict(self._base_headers)
        headers["content-type"] = "application/octet.stream"
        headers["content-length"] = str(os.path.getsize(src_file_path))
        headers['content-disposition'] = 'attachment; filename=' + dst_name
        if put:
            method = 'PUT'
            uri = self.make_uri(container, dst_name, None)
        else:
            method = 'POST'
            uri = self.make_uri(container, None, None)
        with open(src_file_path, 'rb') as up_file:
            return self.__upload_http(method, headers, uri, up_file)

    ###########################################################################
    # private methods
    #

    def __transact_http(self, method, uri, params, accept):
        headers = dict(self._base_headers)
        if accept:
            headers['Accept'] = accept
        if params:
            headers["Content-type"] = "application/x-www-form-urlencoded"
            params = urlencode(params)

        if self._dbg_print:
            print('===> %s %s' % (method, uri))
            print('  --- Headers ---')
            for k, v in headers.items():
                print('    %s: %s' % (k, v))
            if params:
                print('  --- Params ---')
                print('   ', params)

        conn = HTTPConnection(self._server, self._port)
        conn.connect()
        conn.request(method, uri, params, headers)
        rsp = conn.getresponse()
        status = rsp.status
        data = None
        if self._dbg_print:
            print('===> response status:', status)

        if status != 204:
            if self._dbg_print:
                print('===> response content-type:',
                      rsp.getheader('content-type'))
            ctype = rsp.getheader('content-type')
            if ctype and ctype.startswith('application/json'):
                json_data = rsp.read()
                if self._dbg_print:
                    print('===> JSON DATA:', json_data)
                if json_data:
                    try:
                        if sys.version < '3':
                            # Py2.7
                            data = RestHttp._uc_to_str(json.loads(json_data))
                        else:
                            data = json.loads(json_data.decode('utf-8'))
                    except ValueError:
                        data = {'code': -1, 'detail': json_data}
            else:
                data = rsp.read()

        conn.close()

        if status >= 300:
            if data:
                if isinstance(data, dict):
                    code = data.get('code', -1)
                    if 'detail' in data:
                        detail = data['detail']
                    elif 'message' in data:
                        detail = data['message']
                    else:
                        detail = 'unknown error: ' + str(data)
                else:
                    code = -1
                    detail = 'unknown error: ' + str(data)
            else:
                code = -1
                detail = ''
            raise RestHttpError(status, code, detail)

        return status, data

    def __encode_multipart(self, file_path, file_name, fields=None):
        BOUNDARY = '----------ThE_fIlE_bOuNdArY_$'
        body = []
        if fields:
            for key, val in fields:
                body.append('--' + BOUNDARY)
                body.append('Content-Disposition: form-data; name="%s"' % key)
                body.append('')
                body.append(val)

        with open(file_path, 'rb') as up_file:
            file_content = up_file.read()

        body.append('--' + BOUNDARY)
        body.append(
            'Content-Disposition: form-data; name="file"; filename="%s"'
            % file_name)
        body.append('Content-Type: application/octet-stream')
        body.append('')
        body.append(file_content)

        body.append('--' + BOUNDARY + '--')
        body.append('')
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, '\r\n'.join(body)


    def __upload_http(self, method, headers, uri, body):
        if self._dbg_print:
            print('===> %s %s' % (method, uri))
            print('===> HEADERS:')
            for k, v in headers.items():
                print('===>    %s: %s' % (k, v))

        conn = HTTPConnection(self._server, self._port)
        conn.connect()
        conn.request(method, uri, body, headers)

        rsp = conn.getresponse()
        status = rsp.status
        data = None
        if status != 204:
            if self._dbg_print:
                print('===> response content-type:',
                      rsp.getheader('content-type'))
            if rsp.getheader('content-type').startswith('application/json'):
                json_data = rsp.read()
                if self._dbg_print:
                    print('===> JSON DATA:', json_data)
                if json_data:
                    try:
                        if sys.version < '3':
                            # Py2.7
                            data = RestHttp._uc_to_str(json.loads(json_data))
                        else:
                            data = json.loads(json_data.decode('utf-8'))
                    except ValueError:
                        data = {'code': -1, 'detail': json_data}
            else:
                data = rsp.read()

        conn.close()
        if status >= 300:
            if data:
                if isinstance(data, dict):
                    code = data.get('code', -1)
                    if 'detail' in data:
                        detail = data['detail']
                    elif 'message' in data:
                        detail = data['message']
                    else:
                        detail = 'unknown error: ' + str(data)
                else:
                    code = -1
                    detail = 'unknown error: ' + str(data)
            else:
                code = -1
                detail = ''
            raise RestHttpError(status, code, detail)

        return status, data

    @staticmethod
    def _uc_to_str(data):
        if isinstance(data, dict):
            return {RestHttp._uc_to_str(k): RestHttp._uc_to_str(v)
                    for k, v in data.iteritems()}
        elif isinstance(data, list):
            return [RestHttp._uc_to_str(i) for i in data]
        elif isinstance(data, unicode):
            return str(data)
        return data
