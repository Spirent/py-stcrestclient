"""
Retrieve STC and API information from a system running a TestCenter server.

This module is provided as a convenient command line tool to get information
about a TestCenter server.

"""
from __future__ import absolute_import
from __future__ import print_function

import sys

if sys.version_info < (2, 7):
    print("requires python2.7 or later", file=sys.stderr)
    sys.exit(1)

try:
    from . import stchttp
except ValueError:
    import stchttp


def stc_system_info(stc_addr):
    """Return dictionary of STC and API information.

    If a session already exists, then use it to get STC information and avoid
    taking the time to start a new session.  A session is necessary to get
    STC information.

    """
    stc = stchttp.StcHttp(stc_addr)
    sessions = stc.sessions()
    if sessions:
        # If a session already exists, use it to get STC information.
        stc.join_session(sessions[0])
        sys_info = stc.system_info()
    else:
        # Create a new session to get STC information.
        stc.new_session('anonymous')
        try:
            sys_info = stc.system_info()
        finally:
            # Make sure the temporary session in terminated.
            stc.end_session()

    return sys_info


def main():
    if len(sys.argv) < 2:
        print('missing TestCenter server address.\n'
              'Usage:', sys.argv[0], 'stc_address', file=sys.stderr)
        return 1

    try:
        sys_info = stc_system_info(sys.argv[1])
        for k in sys_info:
            print('%s: %s' % (k, sys_info[k]))
    except Exception as e:
        print('ERROR', e, file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
