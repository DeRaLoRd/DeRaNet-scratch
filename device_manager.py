from typing import Dict, List

from snmp_manager import MonitoringManager


class Device:
    def __init__(self, ip, metrics_list: List[str]=None):
        self.ip = ip
        self.metrics_list = metrics_list

# TODO: Start using Device class
class DeviceManager:
    def __init__(self, device_list: List[str]=None, mon_manager: MonitoringManager=None):
        self.__id_counter = 0
        self.__device_list = None
        if device_list is not None:
            for address in device_list:
                self.add_device(address)

        self.mon_manager = mon_manager

    @property
    def id_counter(self):
        return self.__id_counter

    @property
    def device_list(self):
        return self.__device_list

    @device_list.setter
    def device_list(self, device_list):
        self.__device_list = device_list

    def add_device(self, address):
        if self.device_list is None:
            self.device_list = []
        item = {
            "id": self.id_counter,
            "ip": address
        }
        self.__id_counter += 1
        self.device_list.append(item)

        self.mon_manager.update_device_list(self.device_list)

    def delete_device(self, removing_id):
        if self.device_list is None:
            return False

        self.device_list = [item for item in self.device_list if item["id"] != removing_id]

        self.mon_manager.update_device_list(self.device_list)

        return True
