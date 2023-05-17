import logging
from utils.config import Config
from utils.enums import LogLevels


class Logger:

    config = Config()

    def __init__(self, logname):
        self.logname = logname

    def log(self, msg, log_level):

        logging.basicConfig(filename='{}{}.log'.format(self.config.logpath,self.logname), filemode='a', format='%(asctime)s - %(message)s', 
                        level=log_level.value)

        if log_level is not LogLevels.INFO:
            print("[{}] {}".format(log_level, msg))

        logging.info(msg)
