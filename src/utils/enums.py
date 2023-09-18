from enum import Enum
import logging

class ConfigKey(str, Enum):
	DEFAULT = "DEFAULT"
	MOVE_STEP = "MOVE_STEP"
	MOVE_COEFICIENT = "MOVE_COEFICIENT"
	PATH = "PATH"
	LOGGER = "LOGGER"
	MODEL = "MODEL"
	OS = "OS"
	DEVICE = "DEVICE"

class LogLevels(Enum):

    INFO = logging.INFO
    WARN = logging.WARN
    ERR = logging.ERROR
