import os
import yaml
from utils.enums import ConfigEnum as CE

class Config:

	__config_file = os.getcwd()+ '/config/general.yaml'
	__devices_db = os.getcwd()+ '/config/devices.yaml'

	def __read_yaml(self, file):
		with open(file, "r") as f:
			return yaml.safe_load(f)

	@property
	def get_device_os(self):
		return self.__read_yaml(self.__config_file)[CE.DEVICE][CE.OS]

	@property
	def get_device_model(self):
		return self.__read_yaml(self.__config_file)[CE.DEVICE][CE.MODEL]

	@property
	def logpath(self):
		return self.__read_yaml(self.__config_file)[CE.LOGGER][CE.PATH]

	@property
	def step_size(self):
		device = self.__read_yaml(self.__config_file)[CE.DEVICE]
		if device[CE.OS] == CE.DEFAULT:
			return self.__read_yaml(self.__devices_db)[CE.DEVICE][device[CE.OS]][CE.MOVE_STEP]
		return self.__read_yaml(self.__devices_db)[CE.DEVICE][device[CE.OS]][device[CE.MODEL]][CE.MOVE_STEP]

	@property
	def get_step_coeficient(self):
		device = self.__read_yaml(self.__config_file)[CE.DEVICE]
		if device[CE.OS] == CE.DEFAULT:
			return self.__read_yaml(self.__devices_db)[CE.DEVICE][device[CE.OS]][CE.MOVE_COEFICIENT]
		return self.__read_yaml(self.__devices_db)[CE.DEVICE][device[CE.OS]][device[CE.MODEL]][CE.MOVE_COEFICIENT]
