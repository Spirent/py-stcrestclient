from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))


def create_ports(stc):
    print('Create a Project - root')
    project = stc.create('project')
    print('project handle:', project)

    print('\nGet Project attributes')
    project_name = stc.get(project, 'name')
    print('project name:', project_name)

    print('\nCreate Port 1 under', project)
    port1 = stc.create('port', project)
    print('port 1 handle:', port1)

    print('\nCreate Port 2 under', project)
    port2 = stc.create('port', project)
    print('port 2 handle:', port2)


if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    create_ports(stc)
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
