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

def createBGPConfig():
    for i in range(1, PORT_NUMBER+1):
        portHdl=stc.create("port", under="project1", name="myport_%d"%i)
        retData = stc.perform("DeviceCreateCommand",
                        DeviceType="EmulatedDevice",
                        ParentList="project1",
                        CreateCount=DEVICE_NUMBER_PER_PORT,
                        Port=portHdl,
                        IfStack="Ipv4If VlanIf EthIIIf Ipv6If",
                        IfCount="1 1 1 1")
        devHdlList = retData['ReturnList'].split()
        #print("dev list:", devHdlList)
        #stc.config("emulateddevice1001.ipv4if", Address="10.1.1.13", Gateway="10.1.1.1")
        j=1
        for devHdl in devHdlList:
            #print("Create Device BGP:", devHdl)
            bgpcfghdl = stc.create("BgpRouterConfig",
                       under=devHdl,
                       AsNum=1111,
                       DutAsNum=2222, name="myBGP_R_%d_%d"%(i,j))
            bgpV4Hdl = stc.create("BgpIpv4RouteConfig", under=bgpcfghdl, AsPath="11%d%d"%(i,j), name="myBGPV4_%d_%d"%(i,j))
            j+=1

# Slow way
def getAllBGPConfigViaLoop():
    start_time = time.time()
    for port in stc.get("project1", "children-port").split():
        for device in stc.get(port, "affiliationport-Sources").split():
            bgpconfig = stc.get(device, "children-BgpRouterConfig")
            #print(bgpconfig)
            if bgpconfig:
                bgpv4List = stc.get(bgpconfig, "children-bgpipv4routeconfig").split()
                for bgproute in bgpv4List:
                    name = stc.get(bgproute, "Name")
                    starting_ip = stc.get(bgproute + ".ipv4networkblock", "StartIpList")
                    #print("==>", name, starting_ip)
    end_time = time.time()
    print(f"===>Time Taken via stc.get in for loop:{end_time - start_time}")

# faster way        
def getAllBGPConfigViaCmd():
    start_time = time.time()
    result = stc.perform("GetObjectsCommand", ClassName="BgpIpv4RouteConfig", PropertyList="Name ipv4networkblock.StartIpList")
    #print(result['PropertyValues'])
    myDict = json.loads(result['PropertyValues'])
    end_time = time.time()
    print(f"===>Time Taken via GetObjectsCommand:{end_time - start_time}")

def getSpecifiedBGPConfigViaRootlist():
    result = stc.perform("GetObjectsCommand", ClassName="BgpIpv4RouteConfig", RootList="emulateddevice1 emulateddevice2", PropertyList="Name ipv4networkblock.StartIpList")
    print("===>", result['PropertyValues'])

def getSpecifiedBGPConfigViaCondition():
    result = stc.perform("GetObjectsCommand", ClassName="BgpIpv4RouteConfig", Condition="AsPath='1114' OR AsPath='1123'", PropertyList="Name ipv4networkblock.StartIpList")
    print("===>",result['PropertyValues'])


if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])
    stc.join_session(session_id)
    createBGPConfig()
    print("===>Finished BGP Configurations....")
    getAllBGPConfigViaLoop()
    getAllBGPConfigViaCmd()
    getSpecifiedBGPConfigViaRootlist()
    getSpecifiedBGPConfigViaCondition()
    
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
