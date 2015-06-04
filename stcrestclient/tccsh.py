"""
Spirent TestCenter Command Shell

Interactive command shell that provides Session Manager and Automation API
functionality using a command line interface.  This command accesses a
TestCenter Server over its HTTP interface, so no local BLL installation is
needed.

Type help to see help info.  Use <TAB> for command auto-completion.

"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import socket
import cmd
import shlex

try:
    from . import stchttp
    from . import resthttp
except ValueError:
    import stchttp
    import resthttp

if sys.hexversion < 0x03000000:
    input = raw_input


class TestCenterCommandShell(cmd.Cmd):

    intro = 'Welcome to Spirent TestCenter Command Shell (tccsh)'
    _stc = None
    _joined = None
    _sessions = []
    _server = None
    _port = None

    def preloop(self):
        # Do this once before entering command loop.
        self._update_sessions()
        self.postcmd(None, None)

    def postcmd(self, stop, line):
        # Do this after executing each command.
        if self._joined:
            self.prompt = '%s:%s> ' % (self._server, self._joined)
        else:
            self.prompt = '%s:> ' % (self._server,)
        return stop

    def do_ls(self, s):
        """List current sessions.
        -l    List session info with each session.
        """
        self._update_sessions()
        info = (s == '-l')
        for session in self._sessions:
            if session == self._joined:
                print('  [%s] <-- current session' % (session,))
            else:
                print(' ', session)
            if info:
                self.do_info(session)

    def do_info(self, session):
        """Show information about the specified session: info testA - jdoe"""
        if not session:
            session = self._joined
            if not session:
                print('no session specified')
                return
        info = self._stc.session_info(session)
        for k in info:
            print('  %s: %s' % (k, info[k]))

    def complete_info(self, text, line, begidx, endidx):
        return self._complete_session(text)

    def do_delete(self, session):
        """Delete the specified session: delete testA - jdoe"""
        if self._not_session(session):
            return
        if session == self._joined:
            print('you must first end this session')
            return
        try:
            self._stc.join_session(session)
            self._stc.end_session()
        except RuntimeError as e:
            print(e)

    def complete_delete(self, text, line, begidx, endidx):
        return self._complete_session(text)

    def do_delete_all(self, session):
        """Delete all sessions from server."""
        self._update_sessions()
        for session in self._sessions:
            if session != self._joined:
                print('Deleting session:', session)
                self.do_delete(session)

    def do_new(self, s):
        """Create a new session: new user_name session_name"""
        if self._joined is not None:
            # End the current session, without deleting TC session.
            self._stc.end_session(False)
            self._joined = None
        params = s.split()
        if params:
            user_name = params.pop(0)
        else:
            user_name = 'anonymous'
        if params:
            session_name = params.pop(0)
        else:
            session_name = None
        try:
            sid = self._stc.new_session(user_name, session_name)
        except Exception as e:
            print(e)
            return
        self._update_sessions()
        self._joined = sid
        print('Created and joined session:', sid)

    def do_files(self, s):
        """List the files available in the current session."""
        if self._not_joined():
            return
        for f in self._stc.files():
            print(' ', f)

    def do_join(self, session):
        """Join the specified session: join testA - jdoe"""
        if self._not_session(session):
            return
        try:
            bll_ver = self._stc.join_session(session)
        except Exception as e:
            print(e)
            return
        bll_ver = self._stc.join_session(session)
        self._joined = session
        print('Joined session "%s" (BLL ver: %s)' % (session, bll_ver))

    def complete_join(self, text, line, begidx, endidx):
        return self._complete_session(text)

    def do_debug_on(self, s):
        """Enable debug printing."""
        self._stc.enable_debug_print()

    def do_debug_off(self, s):
        """Disable debug printing."""
        self._stc.disable_debug_print()

    def do_exit(self, s):
        """Exit the SessionManager shell."""
        return True

    def do_end(self, end_tcsession):
        """End the current session."""
        if self._not_joined():
            return
        yn = self._confirm('End test session', self._joined)
        try:
            self._stc.end_session(yn)
        except RuntimeError as e:
            print(e)
        self._joined = None

    def do_server(self, server):
        """Specify STC server.

        If a port is not specified, then the value of the STC_SERVER_PORT
        environment variable is used.  If that is not set, then the default
        port 8888 is tried.  If a connection cannot be make to 8888, then port
        80 is used.

        Synopsis:
            server server_address [port]

        Example:
            server 10.109.120.84 80

        """
        server_ok = False
        while not server_ok:
            while not server:
                server = input('Enter server: ')
            try:
                socket.gethostbyname(server)
                server_ok = True
            except socket.gaierror as e:
                print(e)
                server = None

        try:
            self._stc = stchttp.StcHttp(
                server, debug_print=self._stc.debug_print())
        except RuntimeError as e:
            print(e)
            return

        self._server = server
        self._joined = None
        self._sessions = []

    def do_upgrade(self, s):
        """Upgrade server."""
        print("not implemented")

    def do_results(self, s):
        """Get result files from test session."""
        print("not implemented")

    def do_upload(self, file_path):
        """Upload a file to the session: upload sample.tcc"""
        if self._not_joined():
            return

        if file_path:
            if not os.path.isfile(file_path):
                print('file not found:', file_path)
                return
        else:
            while not file_path:
                file_path = input('upload file: ')
                if not file_path:
                    continue
                if not os.path.isfile(file_path):
                    print('file not found:', file_path)
                    return

        try:
            upload_info = self._stc.upload(file_path)
        except (resthttp.RestHttpError, RuntimeError) as e:
            print(e)
            return

        print('uploaded file:', file_path)
        for k in upload_info:
            print('  %s: %s' % (k, upload_info[k]))

    def do_download(self, file_name):
        """Download a file from the session: download bll.session.log"""
        if self._not_joined():
            return

        def check_path(save_path):
            save_name = os.path.basename(save_path)
            if os.path.isdir(save_name):
                print(save_name, 'is a directory')
                return None
            if os.path.isfile(save_name):
                yn = self._confirm('overwrite', save_name)
                if not yn:
                    return None
            return save_name

        save_name = check_path(file_name) if file_name else None
        while not save_name:
            save_name = input('save file as: ')
            if save_name:
                save_name = check_path(save_name)

        try:
            save_name, bytes = self._stc.download(file_name)
        except RuntimeError as e:
            print(e)
            return

        print('wrote %s bytes to %s' % (bytes, save_name))

    def complete_download(self, text, line, begidx, endidx):
        files = self._stc.files()
        if not text:
            return files
        return [f for f in files if f.startswith(text)]

    def do_system_info(self, args):
        """Shows information about the connected STC system.

        The STC (BLL) version is only available if a current session is active.

        """
        sys_info = self._stc.system_info()
        for k in sys_info:
            print('  ', k, ': ', sys_info[k], sep='')

    ###########################################################################
    # Automation API
    #

    def do_stc_apply(self, s):
        """Send test configuration to chassis."""
        if self._not_joined():
            return
        try:
            self._stc.apply()
        except resthttp.RestHttpError as e:
            print('error:', e)
            return
        print('OK')

    def do_stc_get(self, args):
        """Returns the value(s) of one or more object attributes.

        Synopsis:
            stc_get handle [attrib, ..]

        Example:
            stc_get system1 version name

        If multiple arguments, this method returns a dictionary of argument
        names mapped to the value returned by each argument.

        If a single argument is given, then the response is a list of values
        for that argument.

        """
        if self._not_joined():
            return
        args = args.split()
        if not args:
            print('missing object handle')
            return
        handle = args.pop(0)
        try:
            result = self._stc.get(handle, *args)
        except resthttp.RestHttpError as e:
            print(e)
            return

        if isinstance(result, dict):
            for k in result:
                print('  ', k, ': ', result[k], sep='')
        else:
            print(' '.join(result))

    def do_stc_create(self, args):
        """Create a new automation object.

        Synopsis:
            stc_create object_type [under] [attribute, ..]

        Example:
            stc_create port project1

        """
        if self._not_joined():
            return
        args = args.split()
        if not args:
            print('missing object type')
            return
        obj_type = args.pop(0)
        under = args.pop(0) if args else None
        try:
            hnd = self._stc.create(obj_type, under, self._args_to_dict(args))
        except resthttp.RestHttpError as e:
            print(e)
            return
        print('created:', hnd)

    def do_stc_perform(self, args):
        """Perform a command.

        Synopsis:
            stc_perform command [param=value, ...]

        Example:
            stc_perform SaveAsXml config=project1 filename=mytest.xml

        """
        if self._not_joined():
            return
        args = shlex.split(args)
        if not args:
            print('missing command')
            return
        cmd = args.pop(0)
        params = self._args_to_dict(args)
        try:
            print(self._stc.perform(cmd, params))
        except resthttp.RestHttpError as e:
            print(e)

    def do_stc_config(self, args):
        """Sets or modifies one or more object attributes or relations.

        Synopsis:
            stc_config handle [name=value, ...]

        Example:
            stc_config port1 location=//10.100.20.60/1/1

        """
        if self._not_joined():
            return
        args = shlex.split(args)
        if not args:
            print('missing object handle')
            return
        handle = args.pop(0)
        try:
            self._stc.config(handle, self._args_to_dict(args))
        except resthttp.RestHttpError as e:
            print(e)
            return
        print('OK')

    def do_stc_delete(self, handle):
        """Delete the specified object.

        Arguments:
        handle -- Handle of object to delete.

        """
        if self._not_joined():
            return
        if not handle:
            print('missing object handle')
            return
        try:
            self._stc.delete(handle)
        except resthttp.RestHttpError as e:
            print(e)
            return
        print('OK')

    def do_chassis(self, param):
        """Get list of chassis known by test session."""
        if self._not_joined():
            return
        try:
            chassis = self._stc.chassis()
        except resthttp.RestHttpError as e:
            print(e)
            return

        for c in chassis:
            print(' ', c)

    def do_chassis_info(self, chassis):
        """Get information about the specified chassis.

        Synopsis:
            chassis_info chassis_addr

        Example:
            chassis_info 10.100.20.60

        """
        if self._not_joined():
            return
        try:
            info = self._stc.chassis_info(chassis)
        except resthttp.RestHttpError as e:
            print('error:', e)
            return

        for k in info:
            print('  ', k, ': ', info[k], sep='')

    def do_connections(self, param):
        """Get the connected status of each chassis in the test session."""
        if self._not_joined():
            return
        ch_conns = self._stc.connections()
        for ch in ch_conns:
            print('  %-15s' % (ch,), 'CONNECTED' if ch_conns[ch] else '-')

    def do_is_connected(self, chassis):
        """Get the connection status of the specified chassis.

        Synopsis:
            is_connected chassis_addr

        Example:
            is_connected 10.100.20.60

        """
        if self._not_joined():
            return
        if self._stc.is_connected(chassis):
            print('chassis', chassis, 'CONNECTED')
        else:
            print('chassis', chassis, 'not connected')

    def do_stc_connect(self, args):
        """Establish connection to one or more chassis.

        Synopsis:
            stc_connect chassis_list

        Example:
            stc_connect 10.100.20.60 10.100.20.61 10.100.20.62

        Given a list of chassis (IP addresses or DNS names), connect the test
        session to each chassis in list.

        """
        if self._not_joined():
            return
        if not args:
            print('missing chassis')
            return
        chassis_list = args.split()
        try:
            chassis = self._stc.connect(chassis_list)
        except resthttp.RestHttpError as e:
            print(e)
            return
        print('connected %s chassis' % (len(chassis),))

    def do_stc_connectall(self, s):
        """Establish connections to all chassis (test ports) in this session.
        """
        if self._not_joined():
            return
        try:
            self._stc.connectall()
        except resthttp.RestHttpError as e:
            print(e)
            return
        print('OK')

    def do_stc_disconnect(self, args):
        """Disconnect one or more chassis

        Synopsis:
            stc_disconnect chassis_list

        Example:
            stc_disconnect 10.100.20.60 10.100.20.61 10.100.20.62

        Given a list of chassis (IP addresses or DNS names), disconnect each
        chassis in the list from the test session.

        """
        if self._not_joined():
            return
        chassis_list = args.split()
        try:
            self._stc.disconnect(chassis_list)
        except resthttp.RestHttpError as e:
            print(e)
            return
        print('disconnected %s chassis' % (len(chassis_list),))

    def do_stc_disconnectall(self, s):
        """Remove connections to all chassis (test ports) in this session."""
        if self._not_joined():
            return
        try:
            self._stc.disconnectall()
        except resthttp.RestHttpError as e:
            print(e)
            return
        print('OK')

    def do_stc_help(self, subject):
        """Get help information about Automation API: help subject

        The following values can be specified for the subject:
            <empty>        -- gets an overview of help.
            commands       -- gets a list of API functions
            <command name> -- get info about the specified command.
            <object type>  -- get info about the specified object type
            <handle value> -- get info about the object type referred to

        """
        try:
            print(self._stc.help(subject))
        except resthttp.RestHttpError as e:
            print(e)

    ###########################################################################
    # Utility methods
    #

    def _update_sessions(self):
        try:
            self._sessions = self._stc.sessions()
        except resthttp.RestHttpError as e:
            print('Error updating sessions:', e)
            raise

    def _complete_session(self, text):
        if not text:
            return self._sessions
        return [s for s in self._sessions if s.startswith(text)]

    def _confirm(self, prompt, value, default=True):
        confirmed = None
        default_input = 'y' if default else 'n'
        while confirmed is None:
            prompt = '%s "%s" (y/n) [%s]: ' % (prompt, value, default_input)
            yn = input(prompt).lower()
            if yn in ('y', 'yes'):
                confirmed = True
            elif yn in ('n', 'no'):
                confirmed = False
            else:
                confirmed = default

        return confirmed

    def _not_joined(self):
        if self._joined is None:
            print('you must first join a session')
            return True
        return False

    def _not_session(self, session):
        if session not in self._sessions:
            print('no such session')
            return True
        return False

    def _args_to_dict(self, args):
        params = {}
        for arg in args:
            if '=' in arg:
                k, v = arg.split('=', 1)
                params[k] = v
            else:
                params[arg] = None
        return params


def main():
    debug = False
    server = None
    port = None
    prg = sys.argv.pop(0)
    while sys.argv:
        arg = sys.argv.pop(0)
        if arg in ('--debug', '-d'):
            debug = True
        elif arg in ('--port', '-p'):
            if not sys.argv:
                print('missing value after', arg, file=sys.stderr)
                print('see:', prg, '--help', file=sys.stderr)
                return 1
            port = int(sys.argv.pop(0))
        elif arg in ('--help', '-h', '-?'):
            print('Usage: ', prg, '[options] server', file=sys.stderr)
            print('Options:', file=sys.stderr)
            print('    -d, --debug  Enable debug output', file=sys.stderr)
            print('    -p, --port  Server port to connect to (default 8888)',
                  file=sys.stderr)
            return 0
        elif arg[0] == '-':
            print('unrecognized argument:', arg, file=sys.stderr)
            print('see:', prg, '--help', file=sys.stderr)
            return 1
        else:
            server = arg

    if debug:
        print('===> connecting to', server, end=' ')
        if port:
            print('on port', port)
        else:
            print()

    server_ok = False
    while not server_ok:
        while not server:
            server = input('Enter server: ')

        try:
            socket.gethostbyname(server)
            server_ok = True
        except socket.gaierror as e:
            print('hostname not known')
            server = None

    tccsh = TestCenterCommandShell()
    tccsh._server = server
    tccsh._port = port
    try:
        tccsh._stc = stchttp.StcHttp(server, port, debug_print=debug)
    except Exception as e:
        print(e)
        return 1

    try:
        tccsh.cmdloop()
    except KeyboardInterrupt:
        print('\nGot keyboard interrupt. Exiting...')

    return 0


if __name__ == '__main__':
    sys.exit(main())
