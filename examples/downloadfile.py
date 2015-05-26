from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))

if len(sys.argv) < 3:
    print('usage: python', sys.argv[0], 'server_addr file', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)

    # Download file.
    download_name = sys.argv[2]
    save_name, bytes = stc.download(download_name)
    print('wrote %s bytes to %s' % (bytes, save_name))

except Exception as e:
    print(e, file=sys.stderr)
    raise
    #sys.exit(1)

