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

    # Upload sample.tcc file.
    file_name = 'sample.tcc'
    data = stc.upload(file_name)
    print('uploaded file:', file_name)
    for k, v in data.items():
        print('    %s: %s' % (k, v))

except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)

