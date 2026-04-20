from pysnmp.hlapi.v3arch.asyncio import *
import asyncio
import platform
import subprocess

class MonitoringManager:
    def __init__(self, ip_list = None, interval = 5):
        self.engine = SnmpEngine()

        if not self.validate_ip_list(ip_list):
            raise RuntimeError("Invalid ip list")
        else:
            self.__ip_list = ip_list

        if interval < 1:
            raise ValueError("Interval must be greater than 1 second")
        else:
            self.__interval = interval

    @property
    def ip_list(self):
        return self.__ip_list

    @ip_list.setter
    def ip_list(self, value):
        if self.validate_ip_list(value):
            self.__ip_list = value

    @property
    def interval(self):
        return self.__interval

    @interval.setter
    def interval(self, value):
        if value < 1:
            raise ValueError("Interval must be greater than 1 second")
        else:
            self.__interval = value

    def validate_ip_list(self, ip_list):
        return True

    def append_ip_list(self, ip):
        if ip not in self.ip_list:
            if self.validate_ip_list(ip):
                self.ip_list.append(ip)
                print("Added " + ip)

    def ping(self, ip):
        if platform.system().lower() == "windows":
            result = subprocess.run(["ping", "-n", "1", ip], stdout=subprocess.PIPE)
        else:
            result = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE)
        return result.returncode

    async def snmp_get(self, ip, community="public", module="SNMPv2-MIB", oid="sysDescr"):
        error_indication, error_status, error_index, response = await get_cmd(
            self.engine,
            CommunityData(community),
            await UdpTransportTarget.create((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(module, oid, 0)))
        if error_indication:
            print("ERROR: " + str(error_indication))
        return response

    async def snmp_poll(self):
        while True:
            for ip in self.ip_list:
                response = await self.snmp_get(ip, "public", "SNMPv2-MIB", "sysUpTime")

                if response:
                    uptime = response[0][1]
                    print(f"{ip} : Uptime: {uptime}")
                else:
                    print(f"{ip} : No response")

            await asyncio.sleep(self.interval)