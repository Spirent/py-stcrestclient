from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))

if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)

    # Delete Port 1
    port1_handle = 'port1'
    stc.delete(port1_handle)
    print('successully deleted', port1_handle)

except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
