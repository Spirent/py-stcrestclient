from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))


def bulkconfig_device(stc):
    port1 = 'port1'
    port2 = 'port2'

    print('Creating emulateddevice on Port 1')
    dev1_handle = stc.create('emulateddevice', 'project1', {'name': 'cdev', 'AffiliationPort-targets': port1})
    print('emulateddevice 1 handle:', dev1_handle)

    print('Configuring the emulateddevice \'cdev\'')
    ret1 = stc.bulkconfig('emulateddevice[@name="cdev"]', {'routeridstep': '0.0.1.0'})
    print(ret1)
    assert str(ret1['status'])=="success"
    assert len(ret1['handles'])== 1  #['emulateddevice1']
    
    print('Configuring ethiiif and ipv4if under the emulateddevice \'cdev\'')
    ethiiif = stc.create('ethiiif', dev1_handle, {'name': 'myethiiif', 'SourceMac': 'be:ef:00:00:02:00'})
    ipv4if = stc.create('ipv4if', dev1_handle, {'name': 'myipv4if', 'Address': '192.85.0.2'})
        
    print('Configuring emulateddevice \'cdev\' and its children')
    ret2 = stc.bulkconfig(dev1_handle, 
                {"PrimaryIf-targets": 'xpath:./Ipv4If', "TopLevelIf": 'Xpath:./Ipv4If',
                'Ethiiif': {'SourceMac': 'be:ef:00:00:03:00',  'name': 'myethiiif1'},
                'ipV4if': {'name': 'myipv4if1', 'Address': '192.85.0.4', 'Gateway': '192.85.0.1'}})
    print(ret2)
    assert str(ret2['status'])=="success"
    assert len(ret2['handles'])== 3 #"['emulateddevice1', 'ethiiif1', 'ipv4if1']" 


if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    bulkconfig_device(stc)
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
