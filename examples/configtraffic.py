from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))


def config_traffic(stc):
    port1 = 'port1'
    port2 = 'port2'

    print('Creating StreamBlock on Port 1')
    sb1_handle = stc.create('streamBlock', port1)
    print('StreamBlock 1 handle:', sb1_handle)

    data = stc.get(port1, 'children-generator')
    print('generator:', ' '.join(data))

    data = stc.get(port2, 'children-analyzer')
    print('analyzer:', ' '.join(data))


if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    config_traffic(stc)
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
