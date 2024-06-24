from __future__ import print_function
import sys
import time
import json
from stcrestclient import stchttp

session_name = 'extest'
user_name = 'someuser'
session_id = ' - '.join((session_name, user_name))


PORT_NUMBER = 2
DEVICE_NUMBER_PER_PORT = 2000

def create_bgpv4():
    for i in range(1, PORT_NUMBER+1):
        port_hdl = stc.create("port", under="project1", name="myport_%d"%i)
        ret_data = stc.perform("DeviceCreateCommand",
                        DeviceType="EmulatedDevice",
                        ParentList="project1",
                        CreateCount=DEVICE_NUMBER_PER_PORT,
                        Port=port_hdl,
                        IfStack="Ipv4If VlanIf EthIIIf Ipv6If",
                        IfCount="1 1 1 1")
        devhdl_list = ret_data['ReturnList'].split()
        #print("dev list:", devHdlList)
        #stc.config("emulateddevice1001.ipv4if", Address="10.1.1.13", Gateway="10.1.1.1")
        j=1
        for devhdl in devhdl_list:
            #print("Create Device BGP:", devHdl)
            bgpcfg_hdl = stc.create("BgpRouterConfig",
                       under=devhdl,
                       AsNum=1111,
                       DutAsNum=2222, name="myBGP_R_%d_%d"%(i,j))
            bgpv4_hdl = stc.create("BgpIpv4RouteConfig", under=bgpcfg_hdl, AsPath="11%d%d"%(i,j), name="myBGPV4_%d_%d"%(i,j))
            j+=1

# Slow way
def get_all_bgpv4_via_loop():
    start_time = time.time()
    for port in stc.get("project1", "children-port").split():
        for device in stc.get(port, "affiliationport-Sources").split():
            bgpconfig = stc.get(device, "children-BgpRouterConfig")
            #print(bgpconfig)
            if bgpconfig:
                bgpv4_list = stc.get(bgpconfig, "children-bgpipv4routeconfig").split()
                for bgproute in bgpv4_list:
                    name = stc.get(bgproute, "Name")
                    starting_ip = stc.get(bgproute + ".ipv4networkblock", "StartIpList")
                    #print("==>", name, starting_ip)
    end_time = time.time()
    print(f"===>Time Taken via stc.get in for loop:{end_time - start_time}")

# faster way 
# Notes: in STC 5.51 and above, GetObjectsCommand supports PropertyList        
def get_all_bgpv4_via_cmd():
    start_time = time.time()
    result = stc.perform("GetObjectsCommand", ClassName="BgpIpv4RouteConfig", PropertyList="Name ipv4networkblock.StartIpList")
    #print(result['PropertyValues'])
    my_dict = json.loads(result['PropertyValues'])
    end_time = time.time()
    print(f"===>Time Taken via GetObjectsCommand:{end_time - start_time}")

def get_specified_bgpv4_via_rootlist():
    result = stc.perform("GetObjectsCommand", ClassName="BgpIpv4RouteConfig", RootList="emulateddevice1 emulateddevice2", PropertyList="Name ipv4networkblock.StartIpList")
    print("===>", result['PropertyValues'])

def get_specified_bgpv4_via_condition():
    result = stc.perform("GetObjectsCommand", ClassName="BgpIpv4RouteConfig", Condition="AsPath='1114' OR AsPath='1123'", PropertyList="Name ipv4networkblock.StartIpList")
    print("===>",result['PropertyValues'])


if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    create_bgpv4()
    print("===>Finished BGP Configurations....")
    get_all_bgpv4_via_loop()
    get_all_bgpv4_via_cmd()
    get_specified_bgpv4_via_rootlist()
    get_specified_bgpv4_via_condition()
    
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
