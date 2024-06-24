from __future__ import print_function
import sys
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))


'''
XPATH Rules:
Operator      Meaning         Examples
---------------------------------------------------------------------
   =          Equal	      /port[@name=Port1]
                              /port[@name="port1"]
*= or ~=      Contain         /port/emulateddevice[@name *= dev]
                              /port/emulateddevice[@name ~= dev]
   ^=         Start with      /port[@name ^= port]/emulateddevice[@name ^= dev]
   !=         NOT Equal       /port[@name != port1]/emulateddevice
   []         Get via Index   /port[1]
'''



def bulkapi_create_ports_and_devices(stc):
    # this is the prerequisites before making bulk config
    # Create two ports
    result = stc.bulkcreate('port', 
        [
            {
                "location": "//(Offline)/1/1",
                "name": "TestPort1",
                "under": "project1"
            },
            {
                "location": "//(Offline)/1/1",
                "name": "TestPort2",
                "under": "project1"
            }
        ])

    # Create four emulateddevices
    result = stc.bulkcreate('emulateddevice', 
        [{
            "name": "myBGPDevd1", 
            "AffiliationPort-targets": "xpath:/port[name='TestPort1']", 
            "under": "project",
            "BgpRouterConfig": {
                "Name":"myBGP_R1",
                "BgpIpv4RouteConfig": [
                    {
                        "Name":"myBGPV4_R1_A"
                    }, 
                    {
                        "Name":"myBGPV4_R1_B"
                    }
                ]
            }
        },
        {
            "name": "myBGPDevd2", 
            "AffiliationPort-targets": "xpath:/port[name='TestPort2']", 
            "under": "project",
            "BgpRouterConfig": {
                "Name": "myBGP_R2", 
                "BgpIpv4RouteConfig": [
                    {
                        "Name":"myBGPV4_R2_A"
                    }, 
                    {
                        "Name":"myBGPV4_R2_B"
                    }
                ]
            }
        },
        {
            "name": "myDevd1", 
            "AffiliationPort-targets": "xpath:/port[name='TestPort1']", 
            "under": "project",
            "IPV4if": {"stackedon": "xpath:./EthIIIf", "name": "myIpv4if1", "Address": "192.85.0.110", "Gateway": "192.85.0.1"},
            "EthIIIf": {"SourceMac": "be:ef:00:00:01:00"}
        },
        {
            "name": "myDevd2", 
            "AffiliationPort-targets": "xpath:/port[name='TestPort2']", 
            "under": "project",
            "IPV4if": {"stackedon": "xpath:./EthIIIf", "name": "myIpv4if2", "Address": "192.85.0.111", "Gateway": "192.85.0.1"},
            "EthIIIf": {"SourceMac": "be:ef:00:00:01:ee"}
        }])
    
    print("Prerequisites: Create Emulateddevices and BGPs finished")

def bulkapi_update_devices_attr(stc):
    # 'emulateddevice3', 'emulateddevice4' will be updated with the same RouterId and RouterIdStep
    result = stc.bulkconfig('emulateddevice[@name^="myDev"]', {"RouterId": "10.5.0.11", "RouterIdStep": "0.0.1.0"})
    print("Update attributes:", result)
    
def bulkapi_update_objects_attr(stc):
    # the emulateddvice whose name start with "myDev"('emulateddevice3' and 'emulateddevice4' in this example) will be updated
    # the objects of Ethiiif and ipV4if under each devices will be updated too.
    result = stc.bulkconfig('emulateddevice[@name^="myDev"]',
                          {
                              "PrimaryIf-targets": "xpath:./Ipv4If", "TopLevelIf": "Xpath:./Ipv4If",
                              "Ethiiif": {"SourceMac": "be:ef:00:00:03:00"},
                              "ipV4if": {"Address": "192.88.0.10", "Gateway": "192.88.0.1"}
                           })
    print("Update attributes of objects:", result)

def bulkapi_update_attrs_separately(stc):
    # port[0]/emulateddevice will have all emulateddevices under port1 filtered out(Here are emulateddevice1 and emulateddevice3).
    # emulateddevice1 will be updated using the first item in list below.
    # emulateddevice3 will be updated using the second item in the list below.
    result = stc.bulkconfig('port[0]/emulateddevice',
          [
            {"routeridstep": "0.0.3.0", "BgpRouterConfig": {"DutIpv4AddrList": "196.0.1.1"}, "routerid":"196.0.3.5"},
            {"routeridstep": "0.0.0.3", "routerid":"196.0.3.15"}
          ])
    print("Update attributes separately using list:", result)

def bulkapi_update_bgpattr_using_xpath(stc):
    # emulateddevice[@name="myBGPDevd1"]/bgprouterconfig will have bgprouterconfig1 filtered out.
    # this example will update two bgpipv4routeconfigs under bgprouterconfig1 separately using xpath.
    result = stc.bulkconfig('emulateddevice[@name="myBGPDevd1"]/bgprouterconfig',
        {
            "bgpipv4routeconfig[name=myBGPV4_R1_A]": {
                "NextHopIncrement": "0.0.1.0", 
                "Ipv4networkblock": {"prefixlength": 16}
            },
            "bgpipv4routeconfig[name=myBGPV4_R1_B]": {
                "NextHopIncrement": "0.0.2.0", 
                "Ipv4networkblock": {"prefixlength": 32}
            }
        })
    print("Update All bgpipv4routeconfig Attributes separately using xpath:", result)

def bulkapi_update_one_bgpattr_using_xpath(stc):
    # Two bgpipv4routeconfigs will be filtered out.
    # In this case, only one with name equal to myBGPV4_R2_B is updated.
    result = stc.bulkconfig('emulateddevice[1]',
        {
            "bgprouterconfig/bgpipv4routeconfig[name=myBGPV4_R2_B]": {
                "NextHopIncrement": "0.0.6.0", 
                "Ipv4networkblock": {"prefixlength": 20}
            }
        })
    print("Update One bgpipv4routeconfig Attributes:", result)


if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    bulkapi_create_ports_and_devices(stc)
    bulkapi_update_devices_attr(stc)
    bulkapi_update_objects_attr(stc)
    bulkapi_update_attrs_separately(stc)
    bulkapi_update_bgpattr_using_xpath(stc)
    bulkapi_update_one_bgpattr_using_xpath(stc)
    
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
