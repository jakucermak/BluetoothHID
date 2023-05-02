import logging
from enum import Enum


class LogLevels(Enum):

    INFO = logging.INFO
    WARN = logging.WARN
    ERR = logging.ERROR

class Logger:

    def __init__(self, logname):
        self.logname = logname

    def log(self, msg, log_level):

        logging.basicConfig(filename='{}.log'.format(self.logname), filemode='w', format='%(asctime)s - %(message)s', 
                        level=log_level.value)

        if log_level is not LogLevels.INFO:
            print("[{}] {}".format(log_level, msg))

        logging.info(msg)
