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

    # Download file.
    download_name = 'bll.log'
    file_data = stc.download(download_name)
    with open(download_name, 'w') as save_file:
        save_file.write(file_data)
    print('wrote %s bytes to %s' % (len(file_data), download_name))

except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)

