from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'

if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])

    # Print session information.
    sessions = stc.sessions()
    for session in sessions:
        print(session)
        info = stc.session_info(session)
        for k, v in info.items():
            print('    %s: %s' % (k, v))

except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
