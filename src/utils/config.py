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
    def move_speed(self):
        try:
            return self.__read_yaml(self.__devices_db)[ConfigKey.DEVICE][self.device_os][self.device_model][ConfigKey.MOVE_SPEED]
        except:
            return 1.0

    @property
    def step_coeficient(self):
        try:
            return self.__read_yaml( self.__devices_db)[ConfigKey.DEVICE][self.device_os][ConfigKey.MOVE_COEFICIENT]
        except yaml.YAMLError as e:
            return 1.0

                    ###OLD CODE BLOCK###
    # device = self.__read_yaml(self.__config_file)[ConfigKey.DEVICE]
    # if device[ConfigKey.OS] == ConfigKey.DEFAULT:
    #     return self.__read_yaml(self.__devices_db)[ConfigKey.DEVICE][device[ConfigKey.OS]][ConfigKey.MOVE_COEFICIENT]
    # return self.__read_yaml(self.__devices_db)[ConfigKey.DEVICE][device[ConfigKey.OS]][device[ConfigKey.MODEL]][ConfigKey.MOVE_COEFICIENT]
