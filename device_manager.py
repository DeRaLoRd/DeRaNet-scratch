class Device:
    def __init__(self, ip, metrics_list=None):
        self.ip = ip
        self.metrics_list = metrics_list

class DeviceManager:
    def __init__(self, device_list=None):
        if device_list is None:
            self.__device_list = []
        else:
            self.__device_list = device_list

    @property
    def device_list(self):
        return self.__device_list

    @device_list.setter
    def device_list(self, device_list):
        self.__device_list = device_list

    def add_device(self, device: Device):
        self.__device_list.append(device)