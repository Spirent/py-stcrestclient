from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))


def config_ports(stc):
    port1 = 'port1'
    port2 = 'port2'
    chassis_addr = '10.100.20.60'
    slot = 2
    p1 = 1
    p2 = 2

    loc = "//%s/%s/%s" % (chassis_addr, slot, p1)
    print('Configure Port 1 location:', loc)
    stc.config(port1, {'location': loc})

    loc = "//%s/%s/%s"%(chassis_addr, slot, p2)
    print('Configure Port 2 location:', loc)
    stc.config(port2, location=loc)

    # Check location attribute of ports.
    print()
    print('port 1 location:', stc.get(port1, 'location'))
    print('port 2 location:', stc.get(port2, 'location'))


if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    config_ports(stc)
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)

