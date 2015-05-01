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

    # Start session
    sid = stc.new_session(user_name, session_name)
    print('Created new session:', sid)

except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
