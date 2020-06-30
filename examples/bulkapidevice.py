from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))


def bulkapi_device(stc):
    port1 = 'port1'
    port2 = 'port2'

    isbulkserver = stc.has_bulk_ops()

    print('Creating emulateddevice on Port 1')
    dev = stc.create('emulateddevice', 'project1', {'name': 'devd', 'AffiliationPort-targets': port1})  

    print('Creating emulateddevice on Port 1 and its children')
    ret = stc.bulkcreate('emulateddevice', 
                        {'name': 'devbulk', 'AffiliationPort-targets': port1, 'under': "project1", 
                         "PrimaryIf-targets": 'xpath:./Ipv4If',
                         'ipV4if': {'stackedon': 'xpath:./EthIIIf', 'name': 'myipv4if2', 'Address': '192.85.0.4', 'Gateway': '192.85.0.1'},
                         'EthIIIf': {'SourceMac': 'be:ef:00:00:01:00'},
                         'vlanif': [{'vlanid':102, 'name':'vlanif1'}, {'vlanid':103, 'name':'vlanif2'}],})  
    assert str(ret['status'])=="success"
    assert len(ret['handles'])==5
    assert len(ret['objects'])==5

    print('Get emulateddevice attributes name, routerid with depth 2')
    ret = stc.bulkget("emulateddevice[@name^='dev']", ["name", "routerid"], depth=2)
    print(ret)
    assert str(ret['status'])=="success"
    assert ret['objects'][dev]['props']['name']=="devd"

    print('Creating the chidlren under the emulateddevice starting with name \'dev\'')
    ret = stc.bulkcreateex("emulateddevice[@name^='dev']", 
                  [{'ipV4if': {'name': 'myipv4if1', 'Address': '196.81.0.1', 'Gateway': '196.81.0.1'}},
                   {'EthIIIf': {'SourceMac': 'be:00:00:00:01:00'}}], 
				   vlanif=[{'vlanid': 102}, {'vlanid': 103}])
    print(ret)
    assert str(ret['status'])=="success"
    assert len(ret['handles'])==6
    assert len(ret['objects'])==6

    print('Deleting the emulateddevices starting with name \'dev\'')
    ret = stc.bulkdelete("emulateddevice[@name^='dev']")
    assert str(ret['status'])=="success"
    assert len(ret['handles'])==2
    assert len(ret['objects'])==2
      
    print('Creating the emulateddevice with bgp configuration')
    bret = stc.bulkcreate('emulateddevice', 
                {'name': 'devperform', 'AffiliationPort-targets': port1, 'under': 'project1',
                'vlanif': [{'vlanid':102, 'name':'vlanif1'}, {'vlanid':103, 'name':'vlanif2'}],
                'BgpRouterConfig': {'name': 'mybgprouter', 'AsNum': 166,
                                    'BgpAuthenticationParams': {'authentication': 'md5'},
                                    'BgpIpv4RouteConfig': [{'AigpPresent':'True',
                                                            'BgpCustomAttribute': [{'Length': 1},
                                                                                    {'Length':100}]}, 
                                                            {'AigpPresent':'False',
                                                            'BgpCustomAttribute': {'Length': 10}}]
                                                            }}) 
      
    print('perform BgpAdvertiseRouteCommand on the emulateddevice with bgp configuration')
    ret = stc.bulkperform("BgpAdvertiseRouteCommand", 
                              {"routelist": "xpath:emulateddevice[@name='devperform']", 
                              "prefixfilter": "64"})
    print(ret)
    assert str(ret['Name'])=="BGP: Advertise Routes 1"


if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    bulkapi_device(stc)
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
