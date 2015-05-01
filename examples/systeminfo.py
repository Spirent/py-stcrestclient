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

    # Get STC system info.
    sys_info = stc.system_info()
    for k in sys_info:
        print('%s: %s' % (k, sys_info[k]))

except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
