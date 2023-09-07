import os
import yaml


class Config:

    __config_file = os.getcwd() + '/config/general.yaml'
    __devices_db = os.getcwd() + '/config/devices.yaml'

    def __read_yaml(self, file):
        with open(file, "r") as f:
            return yaml.safe_load(f)

    @property
    def device_os(self):
        return self.__read_yaml(self.__config_file)['DEVICE']['OS']

    @property
    def device_model(self):
        return self.__read_yaml(self.__config_file)['DEVICE']['MODEL']

    @property
    def logpath(self):
        return self.__read_yaml(self.__config_file)['LOGGER']['PATH']

    @property
    def step_size(self):
        device = self.__read_yaml(self.__config_file)['DEVICE']
        return self.__read_yaml(self.__devices_db)['DEVICE'][device['OS']][device['MODEL']]['MOVE_STEP']  # pylint: ignore
