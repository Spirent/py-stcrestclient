"""
STC REST API wrapper module.

This module allows python scripts to call the STC Automation API using HTTP.

To specify the HTTP (REST API) server, the client must set the value of the
environment variable STC_SERVER_ADDRESS, or specify the server when creating
the StcHttp object.

"""
from __future__ import absolute_import
from __future__ import print_function

import time
import os
import socket

try:
    from . import resthttp
except ValueError:
    import resthttp

# Use this port if it is not specified when creating StcHttp, or by the
# STC_SERVER_PORT environment variable.
DEFAULT_PORT = 8888
# Use this port if port not specified and default port does not work.
ALT_PORT = 80


class StcHttp(object):

    """
    Spirent TestCenter ReST API wrapper object.

    """

    def __init__(self, server=None, port=None, api_version=1,
                 debug_print=False):
        """Initialize the REST API wrapper object.

        If the port to connect to is not specified by the port argument, or by
        the STC_SERVER_PORT environment variable, then try connecting on the
        DEFAULT_PORT and then the ALT_PORT.

        Arguments:
        server      -- STC REST API server to connect to. None to use environ.
        port        -- HTTP port to connect to server on.  Use environment
                       variable STC_SERVER_PORT or DEFAULT_PORT if None.
        api_version -- What API version to use.
        debug_print -- Enable debug print statements.

        """
        if not server:
            server = os.environ.get('STC_SERVER_ADDRESS')
            if not server:
                raise RuntimeError('STC_SERVER_ADDRESS not set')
        if port:
            try_ports = [port]
        else:
            port = os.environ.get('STC_SERVER_PORT')
            try_ports = [port] if port else [DEFAULT_PORT, ALT_PORT]

        self._dbg_print = bool(debug_print)
        rest = None
        while try_ports:
            port = try_ports.pop(0)
            url = resthttp.RestHttp.url('http', server, port, 'stcapi')
            rest = resthttp.RestHttp(url, debug_print=debug_print)
            try:
                rest.get_request('sessions')
                break
            except (socket.error, resthttp.ConnectionError,
                    resthttp.RestHttpError):
                if not try_ports:
                    raise RuntimeError('Cannot connect to STC server: %s:%s' %
                                       (server, port))

        rest.add_header('X-Spirent-API-Version', str(api_version))
        self._rest = rest
        self._sid = None

    def session_id(self):
        return self._sid

    def new_session(self, user_name, session_name=None, kill_existing=False):
        """Create a new test session.

        The test session is identified by the specified user_name and optional
        session_name parameters.  If a session name is not specified, then the
        server will create one.

        Return:
        True is session started, False if session was already started.

        """
        if self.started():
            return False
        if not session_name:
            session_name = ''
        params = {'userid': user_name, 'sessionname': session_name}
        try:
            status, data = self._rest.post_request('sessions', None, params)
        except resthttp.RestHttpError as e:
            if kill_existing and str(e).find('already exists') >= 0:
                self._sid = ' - '.join((session_name, user_name))
                self.end_session()
            else:
                raise RuntimeError('failed to create session: ' + str(e))

            # Starting session
            if self._dbg_print:
                print('===> starting session')
            status, data = self._rest.post_request('sessions', None, params)
            if self._dbg_print:
                print('===> OK, started')

        sid = data['session_id']
        if self._dbg_print:
            print('===> session ID:', sid)
            print('===> URL:', self._rest.make_url('sessions', sid))

        self._rest.add_header('X-STC-API-Session', sid)
        self._sid = sid
        return sid

    def join_session(self, sid):
        self._rest.add_header('X-STC-API-Session', sid)
        self._sid = sid
        try:
            status, data = self._rest.get_request('objects', 'system1',
                                                  ['version', 'name'])
        except resthttp.RestHttpError as e:
            self._rest.del_header('X-STC-API-Session')
            self._sid = None
            raise RuntimeError('failed to join session: ' + str(e))

        return data['version']

    def end_session(self, end_tcsession=True):
        """End this test session.

        When the session is ended, it is no longer available.  Clients should
        export any result or log files, that they want to preserve, before the
        session is ended.

        Return:
        True if session ended, false if session was not started.

        """
        if not self.started():
            return False

        if self._dbg_print:
            print('===> deleting session:', self._sid)

        sid = self._sid
        self._sid = None
        if end_tcsession:
            try:
                status, data = self._rest.delete_request('sessions', sid)
                if self._dbg_print:
                    print('===> OK - deleted session on server')
            except resthttp.RestHttpError as e:
                raise RuntimeError('failed to end session: ' + str(e))
            time.sleep(7)

        self._rest.del_header('X-STC-API-Session')
        if self._dbg_print:
            print('===> OK - ended client session')
        return True

    def debug_print(self):
        return self._dbg_print

    def enable_debug_print(self):
        self._dbg_print = True
        self._rest.enable_debug_print()

    def disable_debug_print(self):
        self._dbg_print = False
        self._rest.disable_debug_print()

    def started(self):
        """Return True is session is started.  Otherwise, return False."""
        return bool(self._sid)

    def sessions(self):
        """Get a list of active sessions on the server.

        Return:
        List of session ID values, one for each active session on server.

        """
        status, data = self._rest.get_request('sessions')
        return data

    def session_urls(self):
        """Get a list of active sessions on the server.

        Return:
        List of session URLs, one for each active session on server.

        """
        return [self._rest.make_url('sessions', sid)
                for sid in self.sessions()]

    def session_info(self, session_id=None):
        """Get information on session.

        If session_id is None, the default, then return information about this
        session.  If a session ID is given, then get information about that
        session.

        Arguments:
        session_id -- Id of session to get info for, if not this session.

        Return:
        Dictionary of session information.

        """
        if not session_id:
            if not self.started():
                return []
            session_id = self._sid
        status, data = self._rest.get_request('sessions', session_id)
        return data

    def files(self):
        """Get list of files, for this session, on server."""
        self._check_session()
        status, data = self._rest.get_request('files')
        return data

    def file_urls(self):
        """Get list of files, for this session, on server.

        Return:
        List of session URLs, one for each file on server.

        """
        return [self._rest.make_url('files', f) for f in self.files()]

    def bll_version(self):
        """Get the BLL version this session is connected to.

        Return:
        Version string if session started.  None if session not started.

        """
        if not self.started():
            return None
        status, data = self._rest.get_request('objects', 'system1',
                                              ['version', 'name'])
        return data['version']

    def system_info(self):
        status, data = self._rest.get_request('system')
        return data

    def server_info(self):
        status, data = self._rest.get_request('objects', 'system1')
        return data

    def apply(self):
        """Send test configuration to chassis."""
        self._check_session()
        self._rest.put_request(None, 'apply')

    def get(self, handle, *args):
        """Returns the value(s) of one or more object attributes.

        If multiple arguments, this method returns a dictionary of argument
        names mapped to the value returned by each argument.

        If a single argument is given, then the response is a list of values
        for that argument.

        Arguments:
        handle -- Handle that identifies object to get info for.
        *args  -- Zero or more attributes or relationships.

        Return:
        If multiple args:
        {attrib_name:attrib_val, attrib_name:attrib_val, ..}

        If single arg:
        [handle1, handle1, ..]

        """
        self._check_session()
        status, data = self._rest.get_request('objects', str(handle), args)
        if len(args) == 1 and not isinstance(data, (list, tuple)):
            data = data.split()

        return data

    def create(self, object_type, under=None, attributes=None):
        """Create a new automation object.

        Arguments:
        object_type -- Type of object to create.
        under       -- Handle of the parent of the new object.
        attributes  -- Dictionary of attributes (name-value pairs).

        Return:
        Handle of newly created object.

        """
        data = self.createx(object_type, under, attributes)
        return data['handle']

    def createx(self, object_type, under=None, attributes=None):
        """Create a new automation object.

        Arguments:
        object_type -- Type of object to create.
        under       -- Handle of the parent of the new object.
        attributes  -- Dictionary of attributes (name-value pairs).

        Return:
        Dictionary containing handle of newly created object.

        """
        self._check_session()
        params = {'object_type': object_type}
        if under:
            params['under'] = under
        if attributes:
            params.update(attributes)

        status, data = self._rest.post_request('objects', None, params)
        return data

    def delete(self, handle):
        """Delete the specified object.

        Arguments:
        handle -- Handle of object to delete.

        """
        self._check_session()
        self._rest.delete_request('objects', str(handle))

    def perform(self, command, params=None):
        """Execute a command.

        Arguments:
        command -- Command to execute.
        params  -- Optional.  Dictionary of parameters (name-value pairs).

        Return:
        Data from command.

        """
        self._check_session()
        if not params:
            params = {}
        params['command'] = command
        status, data = self._rest.post_request('perform', None, params)
        return data

    def config(self, handle, attributes=None):
        """Sets or modifies one or more object attributes or relations.

        Arguments:
        handle     -- Handle of object to modify.
        attributes -- Dictionary of attributes (name-value pairs).

        """
        self._check_session()
        self._rest.put_request('objects', str(handle), attributes)

    def chassis(self):
        """Get list of chassis known to test session."""
        self._check_session()
        status, data = self._rest.get_request('chassis')
        return data

    def chassis_info(self, chassis):
        """Get information about the specified chassis."""
        self._check_session()
        status, data = self._rest.get_request('chassis', chassis)
        return data

    def connections(self):
        """Get list of connections."""
        self._check_session()
        status, data = self._rest.get_request('connections')
        return data

    def is_connected(self, chassis):
        """Get Boolean connected status of the specified chassis."""
        self._check_session()
        try:
            status, data = self._rest.get_request('connections', chassis)
        except resthttp.RestHttpError as e:
            if int(e) == 404:
                # 404 NOT FOUND means the chassis in unknown, so return false.
                return False
        return bool(data and data.get('IsConnected'))

    def connect(self, chassis_list):
        """Establish connection to one or more chassis.

        Arguments:
        chassis_list -- List of chassis (IP addresses or DNS names)

        Return:
        List of chassis addresses.

        """
        self._check_session()
        if len(chassis_list) == 1:
            status, data = self._rest.put_request(
                'connections', chassis_list[0])
            data = [data]
        else:
            params = {chassis: True for chassis in chassis_list}
            params['action'] = 'connect'
            status, data = self._rest.post_request('connections', None, params)
        return data

    def disconnect(self, chassis_list):
        """Remove connection with one or more chassis.

        Arguments:
        chassis_list -- List of chassis (IP addresses or DNS names)

        """
        if not isinstance(chassis_list, (list, tuple, set, dict, frozenset)):
            chassis_list = (chassis_list,)

        self._check_session()
        if len(chassis_list) == 1:
            self._rest.delete_request('connections', chassis_list[0])
        else:
            params = {chassis: True for chassis in chassis_list}
            params['action'] = 'disconnect'
            self._rest.post_request('connections', None, params)

    def connectall(self):
        """Establish connections to all chassis (test ports) in this session.

        """
        self._check_session()
        self._rest.post_request('connections', None, {'action': 'connectall'})

    def disconnectall(self):
        """Remove connections to all chassis (test ports) in this session.

        """
        self._check_session()
        self._rest.post_request('connections', None,
                                {'action': 'disconnectall'})

    def help(self, subject=None):
        """Get help information about Automation API.

        The following values can be specified for the subject:
            None -- gets an overview of help.
            'commands' -- gets a list of API functions
            command name -- get info about the specified command.
            object type  -- get info about the specified object type
            handle value -- get info about the object type referred to

        Arguments:
        subject -- Optional.  Subject to get help on.

        Return:
        String of help information.

        """
        if not subject:
            status, data = self._rest.get_request('help')
        else:
            status, data = self._rest.get_request('help', subject)
        return data['message']

    def download(self, file_name):
        """Download the specified file from the server."""
        self._check_session()
        try:
            status, save_name, bytes = self._rest.download_file(
                'files', file_name, None, 'application/octet-stream')
        except resthttp.RestHttpError as e:
            raise RuntimeError('failed to download "%s": %s' % (file_name, e))
        return save_name, bytes

    def upload(self, src_file_path, dst_file_name=None):
        """Upload the specified file to the server."""
        self._check_session()
        status, data = self._rest.upload('files', src_file_path, dst_file_name)
        return data

    def _check_session(self):
        if not self.started():
            raise RuntimeError('must first join session')
