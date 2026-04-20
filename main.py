import asyncio
from snmp_manager import *

async def main():
    print("Begin SNMP scanning")
    print("Setting up continuous polling loop")

    monitoring_manager = MonitoringManager([], 1)
    monitoring_manager.append_ip_list("192.168.1.1")
    monitoring_manager.append_ip_list("demo.pysnmp.com")

    task = asyncio.create_task(monitoring_manager.snmp_poll())
    await task

if __name__ == "__main__":
    asyncio.run(main())