import os
import yaml

from utils.enums import ConfigKey

class Config:

    __config_file = os.getcwd() + '/config/general.yaml'
    __devices_db = os.getcwd() + '/config/devices.yaml'

    def __read_yaml(self, file):
        with open(file, "r") as f:
            return yaml.safe_load(f)

    @property
    def device_os(self):
        return self.__read_yaml(self.__config_file)[ConfigKey.DEVICE][ConfigKey.OS]

    @property
    def device_model(self):
        return self.__read_yaml(self.__config_file)[ConfigKey.DEVICE][ConfigKey.MODEL]

    @property
    def logpath(self):
        return self.__read_yaml(self.__config_file)[ConfigKey.LOGGER][ConfigKey.PATH]

    @property
    def step_size(self):
        device = self.__read_yaml(self.__config_file)[ConfigKey.DEVICE]
        return self.__read_yaml(self.__devices_db)[ConfigKey.DEVICE][device[ConfigKey.OS]][device[ConfigKey.MODEL]][ConfigKey.MOVE_STEP]

    @property
    def step_coeficient(self):
        device = self.__read_yaml(self.__config_file)[ConfigKey.DEVICE]
        if device[ConfigKey.OS] == ConfigKey.DEFAULT:
            return self.__read_yaml(self.__devices_db)[ConfigKey.DEVICE][device[ConfigKey.OS]][ConfigKey.MOVE_COEFICIENT]
        return self.__read_yaml(self.__devices_db)[ConfigKey.DEVICE][device[ConfigKey.OS]][device[ConfigKey.MODEL]][ConfigKey.MOVE_COEFICIENT]
