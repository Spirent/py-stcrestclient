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



def bulkapi_create_ports(stc):
    # Create four ports in this example
    result = stc.bulkcreate('port', 
        [
            {
                "location": "//(Offline)/1/1",
                "name": "Port1",
                "under": "project1"
            },
            {
                "location": "//(Offline)/1/1",
                "name": "Port2",
                "under": "project1"
            },
            {
                "location": "//(Offline)/1/1",
                "name": "TestPort1",
                "under": "project1"
            },
            {
                "location": "//192.168.2.1/1/1",
                "name": "TestPort2",
                "under": "project"
            }
        ])
    print("Create Four Ports:", result)

def bulkapi_create_devices_with_bgp(stc):
    # Create two emulateddevices with AffiliationPort to be port1 and port2
    result = stc.bulkcreate('emulateddevice', 
        [{
            "name": "mydevd1", 
            "AffiliationPort-targets": "port1", 
            "under": "project",
            "PrimaryIf-targets": "xpath:./Ipv4If",
            "ipV4if": {"stackedon": "xpath:./EthIIIf", "name": "myipv4if1", "Address": "192.85.0.4", "Gateway": "192.85.0.1"},
            "EthIIIf": {"SourceMac": "be:ef:00:00:01:00"},
            "vlanif": [
                {"vlanid":102, "name":"vlanif1"}, 
                {"vlanid":103, "name":"vlanif2"}
            ],
            "BgpRouterConfig": {
                "name": "mybgprouter", 
                "AsNum": 166,
                "BgpAuthenticationParams": {"authentication": "md5"},
                "BgpIpv4RouteConfig": [
                    {
                        "AigpPresent":"True",
                        "BgpCustomAttribute": [{"Length": 1},{"Length":100}]
                    }, 
                    {
                        "AigpPresent":"False",
                        "BgpCustomAttribute": {"Length": 10}
                    }
                ]
            }
        },
        {
            "name": "mydevd2", 
            "AffiliationPort-targets": "port2", 
            "under": "project",
            "ipV4if": {"stackedon": "xpath:./EthIIIf", "name": "myipv4if2", "Address": "192.85.0.5", "Gateway": "192.85.0.1"},
            "EthIIIf": {"SourceMac": "be:ef:00:00:01:0e"},
            "vlanif": [
                {"vlanid":102, "name":"vlanif1"}, 
                {"vlanid":103, "name":"vlanif2"}
            ],
            "BgpRouterConfig": {
                "name": "mybgprouter", 
                "AsNum": 167,
                "BgpAuthenticationParams": {"authentication": "md5"},
                "BgpIpv4RouteConfig": [
                    {
                        "AigpPresent":"True",
                        "BgpCustomAttribute": [{"Length": 1},{"Length":100}]
                    }, 
                    {
                        "AigpPresent":"False",
                        "BgpCustomAttribute": {"Length": 10}
                    }
                ]
            }
        }])
    
    print("Create Emulateddevices and BGPs together:", result)


def bulkapi_create_devices_using_xpath(stc):
    # Create two emulateddevices using xpath to set AffiliationPort-targets
    result = stc.bulkcreate('emulateddevice', 
        [{
            "name": "TestDeviceA", 
            "AffiliationPort-targets": "xpath:/port[name='TestPort1']", 
            "under": "project",
        },
         {
            "name": "TestDeviceB", 
            "AffiliationPort-targets": "xpath:/port[name='TestPort2']", 
            "under": "project",
        }])
    print("Create Two Emulateddevices:", result)

    # Create two IF objects under emulateddevice whoes name starts with TestDevice, here it will be emulateddevice4 and emulateddevice5
    # "emulateddevice[@name^='TestDevice']" can also written as "emulateddevice4 emulateddevice5"
    # In the creation below, ipv4if will be created under emulateddevice4 while ethiiif will be created under emulateddevice5.
    # two vlanif objects will be created under each emulateddevice(emulateddevice4 and emulateddevice5 in this example).
    result = stc.bulkcreateex("emulateddevice[@name^='TestDevice']", 
                  [{'ipV4if': {'name': 'myipv4ifA', 'Address': '196.81.0.12', 'Gateway': '196.81.0.1'}},
                   {'EthIIIf': {'SourceMac': 'be:00:00:00:01:00'}}], 
		    vlanif=[{'vlanid': 105}, {'vlanid': 106}])
    print("Create IF objects under emulateddevices:", result)

def bulkapi_get(stc):
    # Get All attributes of the port whose location contains 192.168.2.1
    result = stc.bulkget("port[@location*='192.168.2.1']")
    print("==>Result1:", result)
    # Get Name and RouterId attributes of emulateddevice whose name starts with "mydev"
    result = stc.bulkget("emulateddevice[@name^='mydev']", ["name", "routerid"])
    print("==>Result2:", result)
    # Get Name and AsNum attributes of all BgpRouterConfig
    result = stc.bulkget("BgpRouterConfig", ["Name", "AsNum"])
    print("==>Result3:", result)
    # Get Name attributes of BgpRouterConfig under emulateddevice whose name equal to "mydevd1"
    # if depth is set to 1, only objects of BgpRouterConfig are retrieved.
    # if depth is set to 2, objects of BgpRouterConfig and objects under BgpRouterConfig are retrieved.
    result = stc.bulkget("emulateddevice[name='mydevd1']/BgpRouterConfig", ["Name"], depth=2)
    print("==>Result4:", result)

def bulkapi_perform(stc):
    # Perform BgpAdvertiseRouteCommand using routelist: emulateddevice1 emulateddevice2
    result = stc.bulkperform("BgpAdvertiseRouteCommand", 
                        { "routelist": "xpath:emulateddevice[@name^='mydev']", 
                          "prefixfilter": "64"})
    print("==>Perform BgpAdvertiseRouteCommand:", result)
    # Perform ConfigPropertiesCommand using ObjectList: port3 port4
    result = stc.bulkperform("ConfigPropertiesCommand", 
                        { "ObjectList": "xpath:port[@name^='Test']", 
                          "PropertyList": "generator.generatorConfig.schedulingMode RATE_BASED generator.generatorConfig.durationMode BURSTS"})
    print("==>Perform ConfigPropertiesCommand:", result)

def bulkapi_delete(stc):
    # bulkdelete is quite the same as bulkget. the objects filtered via xpath will be deleted
    result = stc.bulkdelete("emulateddevice[name='mydevd1']/BgpRouterConfig")
    print("Delete the BgpRouterConfig under mydevd1:", result)
    #delete emulateddevices whose name start with mydev
    result = stc.bulkdelete("emulateddevice[@name^='mydev']")
    print("Delete the Emulateddevices with name started with mydev:", result)
    #delete all ports
    result = stc.bulkdelete("port")
    print("Delete all ports:", result)

if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    bulkapi_create_ports(stc)
    bulkapi_create_devices_with_bgp(stc)
    bulkapi_create_devices_using_xpath(stc)
    bulkapi_get(stc)
    bulkapi_perform(stc)
    bulkapi_delete(stc)
    
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
