from pysnmp.hlapi.v3arch.asyncio import *
import asyncio
import platform
import subprocess
import time

def ping(ip):
    if platform.system().lower() == "windows":
        result = subprocess.run(["ping", "-n", "1", ip], stdout=subprocess.PIPE)
    else:
        result = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE)
    return result.returncode

def check_access(ip):
    if ping(ip) == 0:
        print('\t' + ip + " is UP")
    else:
        print('\t' + ip + " is DOWN")

async def snmp_get(ip, community = "public", module = "SNMPv2-MIB", oid = "sysDescr"):
    error_indication, error_status, error_index, response = await get_cmd(
                        SnmpEngine(),
                        CommunityData(community),
                        await UdpTransportTarget.create((ip, 161)),
                        ContextData(),
                        ObjectType(ObjectIdentity(module, oid, 0)))
    if error_indication:
        print("ERROR: " + str(error_indication))
    return response

async def snmp_poll(interval):
    while True:
        response = await snmp_get("192.168.1.1", "public", "SNMPv2-MIB", "sysUpTime")

        # Transfer info to web i guess
        print("Uptime: " + str(response[0][1]))

        await asyncio.sleep(interval)

async def test():
    while True:
        print('lol')
        await asyncio.sleep(3)

async def main():
    print("Begin initialization")
    print("PLATFORM: " + platform.system().lower())
    print("Check localhost access")
    check_access("localhost")
    print("Check router access")
    check_access("192.168.1.1")
    print("Check network access")
    check_access("176.124.220.183")

    print()
    print("Begin SNMP scanning")
    print("Setting up continuous polling loop")

    task1 = asyncio.create_task(snmp_poll(5))
    task2 = asyncio.create_task(test())

    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())